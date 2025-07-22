<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  >

<!-- 
    aim:
      remove the existent structure depending on the configuration file:
        either remove all elements <front>, <body>, <back> and <div> (recurrently) in the entire content of <text>
        or remove only the <div> based structure inside of <body>
        
    CAVEAT:
       This script is part of the larger XProc step "text_injectStructure". It is not to be used independently
       because the result could be an invalid file.
       
    author: Jakub Šimek
-->  
     
  <xsl:output method="xml"/>

  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />
  
  <xsl:param name="structure"></xsl:param>
  
  <!-- the structure configuration to which the parameter $structure indicates the path: -->
  <xsl:variable name="structure_variable" static="no" select="doc($structure)"/>
  
  <xsl:template match="front|body|back">
    <xsl:choose>
      <!-- if the new structure applies to the entire content of <text>
             then all structures therin should be resolved and only their content kept:
        -->
      <xsl:when test="$structure_variable/TEI/text">
        <xsl:apply-templates></xsl:apply-templates>
      </xsl:when>
      <!-- otherwise "front|body|back" shall be kept: -->
      <xsl:otherwise>
        <xsl:copy>
          <xsl:copy-of select="@*"></xsl:copy-of>
          <xsl:apply-templates></xsl:apply-templates>
        </xsl:copy>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <xsl:template match="div">
    <xsl:choose>
      <!-- inside of "body", "div" should always be resolved and only its content kept: -->
      <xsl:when test="ancestor::body">
        <xsl:apply-templates></xsl:apply-templates>
      </xsl:when>
      <!-- inside of "front" or "back", "div" should be resolved (and its content kept)
        only if the structure configuration applies to whole content of "text":      
      -->
      <xsl:when test="(ancestor::front or ancestor::back) and $structure_variable/TEI/text">
        <xsl:apply-templates></xsl:apply-templates>
      </xsl:when>
      <!-- inside of "front" or "back", "div" must not  be resolved 
         if the structure configuration applies only to the content of "body":      
      -->
      <xsl:when test="(ancestor::front or ancestor::back) and $structure_variable/TEI/body">
        <xsl:copy-of select="."></xsl:copy-of>
      </xsl:when>
    </xsl:choose>
  </xsl:template>  
  
</xsl:stylesheet>
