<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.tei-c.org/ns/1.0"
>

  <xsl:output method="xml"/>
  
  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />
  
  <xsl:template match="milestone[tokenize(@ana, '\s+') = 'hc:LineSegmentBeginning'][not(@n)]">
    <xsl:copy>
      <xsl:copy-of select="@*"></xsl:copy-of>
      <xsl:attribute name="n" select="'2'"></xsl:attribute>
    </xsl:copy>
  </xsl:template>

  <!-- Zum Testen -->
  <!-- <xsl:template match="title">
    <xsl:copy><xsl:apply-templates/></xsl:copy>
    <xsl:comment>Testing Pipleine</xsl:comment>
  </xsl:template> -->

</xsl:stylesheet>
