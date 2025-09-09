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
in index entries which have only one appellation element (per language) without a class
this appellation element is marked as hc:PreferredAppellation

-->

  <xsl:output method="xml"/>
  
  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />
  
  <xsl:template match="persName
    [parent::person]
    [not(@ana)]
    [not(@xml:lang)]
    [not(
    preceding-sibling::persName[not(@ana)][not(@xml:lang)] 
    or
    following-sibling::persName[not(@ana)][not(@xml:lang)]
    )]
    |
    persName
    [parent::person]
    [not(@ana)]
    [@xml:lang]
    [not(
    preceding-sibling::persName[not(@ana)][@xml:lang = current()/@xml:lang] 
    or
    following-sibling::persName[not(@ana)][@xml:lang = current()/@xml:lang]
    )]
    |
    placeName
    [parent::place]
    [not(@ana)]
    [not(@xml:lang)]
    [not(
    preceding-sibling::placeName[not(@ana)][not(@xml:lang)] 
    or
    following-sibling::placeName[not(@ana)][not(@xml:lang)]
    )]
    |
    placeName
    [parent::place]
    [not(@ana)]
    [@xml:lang]
    [not(
    preceding-sibling::placeName[not(@ana)][@xml:lang = current()/@xml:lang] 
    or
    following-sibling::placeName[not(@ana)][@xml:lang = current()/@xml:lang]
    )]
    |
    orgName
    [parent::org]
    [not(@ana)]
    [not(@xml:lang)]
    [not(
    preceding-sibling::orgName[not(@ana)][not(@xml:lang)] 
    or
    following-sibling::orgName[not(@ana)][not(@xml:lang)]
    )]
    |
    orgName
    [parent::org]
    [not(@ana)]
    [@xml:lang]
    [not(
    preceding-sibling::orgName[not(@ana)][@xml:lang = current()/@xml:lang] 
    or
    following-sibling::orgName[not(@ana)][@xml:lang = current()/@xml:lang]
    )]
    |
    label
    [parent::item]
    [not(@ana)]
    [not(@xml:lang)]
    [not(
    preceding-sibling::label[not(@ana)][not(@xml:lang)] 
    or
    following-sibling::label[not(@ana)][not(@xml:lang)]
    )]
    |
    label
    [parent::item]
    [not(@ana)]
    [@xml:lang]
    [not(
    preceding-sibling::label[not(@ana)][@xml:lang = current()/@xml:lang] 
    or
    following-sibling::label[not(@ana)][@xml:lang = current()/@xml:lang]
    )]
    |
    title
    [parent::item]
    [not(@ana)]
    [not(@xml:lang)]
    [not(
    preceding-sibling::title[not(@ana)][not(@xml:lang)] 
    or
    following-sibling::title[not(@ana)][not(@xml:lang)]
    )]
    |
    title
    [parent::item]
    [not(@ana)]
    [@xml:lang]
    [not(
    preceding-sibling::title[not(@ana)][@xml:lang = current()/@xml:lang] 
    or
    following-sibling::title[not(@ana)][@xml:lang = current()/@xml:lang]
    )]
    ">
    <xsl:copy>
      <xsl:copy-of select="@*"></xsl:copy-of>
      <xsl:attribute name="ana" select="'hc:PreferredAppellation'"></xsl:attribute>
      <xsl:copy-of select="node()"></xsl:copy-of>
    </xsl:copy>
  </xsl:template>

  

</xsl:stylesheet>
