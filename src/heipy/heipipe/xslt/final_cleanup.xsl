<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0"
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  exclude-result-prefixes="#all"
  >

<!--
    aim:
        Everything we want to remove at the very end
    parameters:
        keep_standOff (xs:boolean, default false()): if true, tei:standOff is kept;
            otherwise it is removed.
    author:
        Gustavo Fernández Riva
-->

  <xsl:output method="xml"/>

  <xsl:param name="keep_standOff" as="xs:boolean" select="false()"/>

  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />

  <xsl:template match="standOff[not($keep_standOff)]"/>

</xsl:stylesheet>
