<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0"
  xmlns="http://www.tei-c.org/ns/1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
>

  <xsl:mode on-no-match="shallow-copy"/>

    <!-- For <add>, <del>, <note> with @facs that are inside line-level content and have no
    <lb> child yet, insert <lb n="1"/> as first child -->
    <xsl:template match="(add|del|note)[@facs]
        [ancestor::l or ancestor::p or ancestor::ab
        or ancestor::head or ancestor::item]
        [not(lb)]">
    <xsl:copy>
        <xsl:copy-of select="@*"/>
        <lb n="1"/>
        <xsl:apply-templates select="node()"/>
    </xsl:copy>
    </xsl:template>


</xsl:stylesheet>
