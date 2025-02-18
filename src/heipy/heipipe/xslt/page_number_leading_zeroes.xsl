<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0"
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  >

<!--
    aim:
          remove leading zeroes from @n in pages

-->

  <xsl:output method="xml"/>

  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />

  <xsl:template match="surface[@ana='hc:Page']/@n">
    <xsl:attribute name="n">
        <xsl:value-of select="replace(., '^0+', '' )"/>
    </xsl:attribute>
  </xsl:template>



</xsl:stylesheet>
