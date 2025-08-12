<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.tei-c.org/ns/1.0"
>

<!--
    aim: wrap all zone elements of a surface in a layout declaration in a <zone ana="hc:VerticalLayout"> if there is more than one zone
    author: Jakub Šimek
-->

  <xsl:output method="xml"/>
  
  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />
  
  <xsl:template match="surface">
    <xsl:copy>
      <xsl:copy-of select="@*"></xsl:copy-of>
      <xsl:copy-of select="graphic"></xsl:copy-of>
      <xsl:choose>
        <xsl:when test="count(zone[not(('hc:InitialZone', 'hc:ImageAnnotationZone') = tokenize(@ana, '\s+'))]) > 1">
          <xsl:element name="zone" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:attribute name="ana" select="'hc:VerticalLayout'"></xsl:attribute>
            <xsl:for-each select="zone[not(('hc:InitialZone', 'hc:ImageAnnotationZone') = tokenize(@ana, '\s+'))]">
              <xsl:copy-of select="."></xsl:copy-of>
            </xsl:for-each>
          </xsl:element>
        </xsl:when>
        <xsl:otherwise>
          <xsl:copy-of select="zone"></xsl:copy-of>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
