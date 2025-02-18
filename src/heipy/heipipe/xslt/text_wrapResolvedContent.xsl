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
  
  <xsl:template match="TEI">
    <xsl:copy>
      <xsl:copy-of select="@*"></xsl:copy-of>
      <xsl:copy-of select="teiHeader"></xsl:copy-of>
      <xsl:copy-of select="facsimile"></xsl:copy-of>
      <xsl:for-each-group select="facsimile/following-sibling::node()" group-adjacent="not(
        self::cb 
        or self::lb 
        or (self::milestone and tokenize(@ana, '\s+') = ('hc:ZoneBeginning', 'hc:ZoneShift', 'hc:LineSegmentBeginning'))
        (:or self::figure[not(tokenize(@ana, '\s+') = 'hc:InlineFigure')]
        or self::table:)
        )" >
        <xsl:choose>
          <xsl:when test="current-grouping-key()">
            <xsl:element name="seg">
              <xsl:attribute name="type" select="'content'"></xsl:attribute>
              <xsl:copy-of select="current-group()"/>
            </xsl:element>
          </xsl:when>
          <xsl:otherwise>
            <xsl:copy-of select="current-group()"/>                        
          </xsl:otherwise>
        </xsl:choose>
      </xsl:for-each-group>
    </xsl:copy>
  </xsl:template>
  
</xsl:stylesheet>
