<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
  xmlns="http://www.tei-c.org/ns/1.0">

<!--
    aim: preparing a listChange element in revisionDesc for the (later) insertion of a change element
    logic:
      - if no revisionDesc is present, it is created as last child of teiHeader and an empty listChange is inserted into it
      - if a revisionDesc is present but without a listChange as a child:  
                - if a change element is present, a listChange is created and all change elements are moved into listChange
                - otherwise the revisionDesc is copied and an empty listChange is inserted into it
      - otherwise the teiHeader is copied unchanged
-->

  <xsl:output method="xml"/>

  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />
  
  <xsl:template match="TEI/teiHeader">
    <!-- copy the teiHeader without its attributes and children -->
    <xsl:copy>
      <!-- copy the teiHeader attributes -->
      <xsl:copy-of select="@*"></xsl:copy-of>
      <xsl:choose>
        <!-- if there is no revisionDesc -->
        <xsl:when test="not(revisionDesc)">
          <!-- copy all present children nodes of the teiHeader -->
          <xsl:copy-of select="*"></xsl:copy-of>
          <!-- create a revisionDesc with empty listChange -->
          <xsl:element name="revisionDesc">
            <xsl:element name="listChange"></xsl:element>
          </xsl:element>
        </xsl:when>
        <!-- if there is revisionDesc -->
        <xsl:otherwise>
          <!-- copy the content of theiHeader and apply templates (if relevant) -->
          <xsl:apply-templates></xsl:apply-templates>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:copy>    
  </xsl:template>
  
  <xsl:template match="revisionDesc">
    <!-- copy the revisionDesc without its attributes and children -->
    <xsl:copy>
      <!-- copy the revisionDesc attributes -->
      <xsl:copy-of select="@*"></xsl:copy-of>
      <xsl:choose>
        <!-- if no listChange is present as a child -->
        <xsl:when test="not(listChange)">
          <!-- copy the present content of revisionDesc without change elements (if there are any) -->
          <xsl:copy-of select="*[not(self::change)]"></xsl:copy-of>
          <!-- create a listChange element and move all change elements into it (if there are any) -->
          <xsl:element name="listChange">
            <xsl:copy-of select="descendant::change"></xsl:copy-of>
          </xsl:element>
        </xsl:when>
        <xsl:otherwise>
          <!-- otherwise copy the present content unchanged -->
          <xsl:apply-templates></xsl:apply-templates>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:copy>    
  </xsl:template>

</xsl:stylesheet>
