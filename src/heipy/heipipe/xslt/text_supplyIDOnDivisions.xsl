<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  >

<!-- 
    aim:
     Supplying @xml:id on front|body|back|div if there is none.
      
    author: 
      Jakub Šimek
-->  
     
  <xsl:output method="xml"/>

  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />
  
  <xsl:template match="front|body|back|div">
    <xsl:choose>
      <xsl:when test="@xml:id">
        <xsl:copy>
          <xsl:copy-of select="@*"></xsl:copy-of>
          <xsl:apply-templates></xsl:apply-templates>
        </xsl:copy>
      </xsl:when>
      <xsl:otherwise>
        <xsl:copy>
          <xsl:copy-of select="@*"></xsl:copy-of>
          <xsl:attribute name="xml:id" select="concat(local-name(), '_', generate-id())"></xsl:attribute>
          <xsl:apply-templates></xsl:apply-templates>
        </xsl:copy>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
</xsl:stylesheet>
