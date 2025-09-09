<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://www.w3.org/1998/Math/MathML"
  xmlns="http://www.tei-c.org/ns/1.0">

<!--
author: Jakub Šimek

aim: 
verbalize machine-readable date information present in certain elements (currently: birth, death) only in att.datable.w3c attributes (@when, @notBefore, @notAfter, @from and @to)  
and write the result into a note element (if no note element is present)

CAVEAT: currently only information in @when in the format JJJJ is being supported (the attribute value is just being copied without any further manipulation)

-->

  <xsl:output method="xml"/>
  
  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />

  <xsl:template match="birth[not(note)]|death[not(note)]">
    <xsl:copy>
      <xsl:copy-of select="@*"></xsl:copy-of>
      <xsl:if test="@when">
        <xsl:element name="note">
          <xsl:value-of select="@when"/>
        </xsl:element>
      </xsl:if>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
