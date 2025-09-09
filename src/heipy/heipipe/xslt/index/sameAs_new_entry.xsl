<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="2.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:xi="http://www.w3.org/2001/XInclude"
  xmlns:svg="http://www.w3.org/2000/svg"
  xmlns:math="http://www.w3.org/1998/Math/MathML"
  xmlns="http://www.tei-c.org/ns/1.0"
  exclude-result-prefixes="math svg xi">

<!--

Autor: Leonhard Maylein

Zweck: Registereinträge mit persName/@type=alternative erhalten eigene person-
       Einträge mit @sameAs-Attribut und dem Alternativnamen als Register-/Indexeintrag

-->

  <xsl:output method="xml"/>

  <xsl:template match="/">
    <xsl:element name="TEI" namespace="http://www.tei-c.org/ns/1.0">
      <xsl:copy-of select="TEI/@*" />
      <xsl:apply-templates select="TEI/*"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="person">
     <xsl:copy-of select="." />
     <xsl:for-each select="./persName[@type='alternative']">
        <xsl:element name="person">
           <xsl:attribute name="sameAs">#<xsl:value-of select="ancestor::person[1]/@xml:id" /></xsl:attribute>
           <xsl:element name="persName"><xsl:attribute name="type">index</xsl:attribute><xsl:value-of select="." /></xsl:element>
           <xsl:element name="persName"><xsl:attribute name="type">alternative</xsl:attribute><xsl:value-of select="ancestor::person[1]/persName[@type='index']" /></xsl:element>
        </xsl:element>
    </xsl:for-each>
  </xsl:template>


  <xsl:template match="@* | *">
    <xsl:copy><xsl:apply-templates select="@* | node()"/></xsl:copy>
  </xsl:template>

</xsl:stylesheet>
