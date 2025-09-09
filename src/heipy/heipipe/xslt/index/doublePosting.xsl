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
index entries with appellation elements marked as hc:AppellationForDoublePosting are duplicated, marked with @sameAs 
and provided with the previous hc:AppellationForDoublePosting as hc:AppellationForDisplayInIndex

-->

  <xsl:output method="xml"/>
  
  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />

  <xsl:template match="person[persName[tokenize(@ana, '\s+') = 'hc:AppellationForDoublePosting']]
    |
    place[placeName[tokenize(@ana, '\s+') = 'hc:AppellationForDoublePosting']]
    |
    org[orgName[tokenize(@ana, '\s+') = 'hc:AppellationForDoublePosting']]
    |
    event[label[tokenize(@ana, '\s+') = 'hc:AppellationForDoublePosting']]
    |
    item[label[tokenize(@ana, '\s+') = 'hc:AppellationForDoublePosting'] or title[tokenize(@ana, '\s+') = 'hc:AppellationForDoublePosting']]">
    <!-- first copy the original entry -->
     <xsl:copy-of select="." />
    <!-- generate duplicates -->
    <xsl:for-each select="*[tokenize(@ana, '\s+') = 'hc:AppellationForDoublePosting']">
        <xsl:element name="{parent::*/local-name()}">
          <!--<xsl:attribute name="xml:id" select="generate-id()"></xsl:attribute>-->
          <xsl:attribute name="sameAs" select="'#' || parent::*/@xml:id"></xsl:attribute>
          <xsl:element name="{local-name()}">
             <xsl:attribute name="ana" select="'hc:PreferredAppellation'"></xsl:attribute>
             <xsl:copy-of select="node()"></xsl:copy-of>
           </xsl:element>
          <xsl:for-each select="parent::*/*[tokenize(@ana, '\s+') = ('hc:AppellationForDisplayInIndex', 'hc:PreferredAppelation')]">
            <xsl:copy>
              <xsl:attribute name="ana" select="'hc:AlternativeAppellation'"></xsl:attribute>
              <xsl:copy-of select="@*[local-name() != 'ana']"></xsl:copy-of>
              <xsl:copy-of select="node()"></xsl:copy-of>
            </xsl:copy>
          </xsl:for-each>
        </xsl:element>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
