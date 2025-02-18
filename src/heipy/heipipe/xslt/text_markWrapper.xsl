<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.tei-c.org/ns/1.0">

  <xsl:output method="xml"/>
  
  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />
  
  <xsl:template match="seg[@type='content']">
    <xsl:copy>
      <xsl:choose>
        <xsl:when test="preceding-sibling::element()[1]/self::lb">
          <xsl:attribute name="type" select="'line'"></xsl:attribute>
        </xsl:when>
        <xsl:when test="preceding-sibling::element()[1]/self::milestone[tokenize(@ana, '\s+') = 'hc:LineSegmentBeginning']">
          <xsl:attribute name="type" select="'line_segment'"></xsl:attribute>
        </xsl:when>
        <xsl:when test="preceding-sibling::element()[1]/self::cb or preceding-sibling::element()[1]/self::milestone[tokenize(@ana, '\s+') = 'hc:ZoneBeginning']">
          <xsl:attribute name="type" select="'zone'"></xsl:attribute>
        </xsl:when>
        <xsl:otherwise>
          <xsl:copy-of select="@type"></xsl:copy-of>
        </xsl:otherwise>
      </xsl:choose>
      <xsl:copy-of select="node()"></xsl:copy-of>
    </xsl:copy>
  </xsl:template>
  
</xsl:stylesheet>
