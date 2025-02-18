<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:math="http://www.w3.org/1998/Math/MathML"
  xmlns="http://www.tei-c.org/ns/1.0">

<!--
    aim: remove whitespace preceding or following line beginnings (lb element), column beginnings (cb), 
        page beginnings (pb) and milestone elements with @ana="hc:ZoneBeginning" or "hc:ZoneShift" 
    note: "whitespace only" text nodes are also being removed because in this neighborhood they are always insignificant 
  
  TODO: consider the treatment of milestone[@ana='hc:LineSegmentBeginning']
-->
  

  <xsl:output method="xml"/>
  
  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />
  
  <xsl:template match="text()" priority="1">
    <xsl:choose>
      <xsl:when test="(name(following-sibling::*[1])=('lb', 'cb', 'pb') 
        or (name(following-sibling::*[1])='milestone' and following-sibling::*[1]/@ana=('hc:ZoneBeginning', 'hc:ZoneShift')))
        and not(
        name(preceding-sibling::*[1])=('lb', 'cb', 'pb') or (name(preceding-sibling::*[1])='milestone' and preceding-sibling::*[1]/@ana=('hc:ZoneBeginning', 'hc:ZoneShift'))
        )">
        <xsl:value-of select="replace(.,'\s+$','')" />
      </xsl:when>
      <xsl:when test="(name(preceding-sibling::*[1])=('lb', 'cb', 'pb') 
        or (name(preceding-sibling::*[1])='milestone' and preceding-sibling::*[1]/@ana=('hc:ZoneBeginning', 'hc:ZoneShift')))
        and not(
        name(following-sibling::*[1])=('lb', 'cb', 'pb') 
        or (name(following-sibling::*[1])='milestone' and following-sibling::*[1]/@ana=('hc:ZoneBeginning', 'hc:ZoneShift'))
        )
        ">
        <xsl:value-of select="replace(.,'^\s+','')" />
      </xsl:when>
      <xsl:when test="(name(following-sibling::*[1])=('lb', 'cb', 'pb') 
        or (name(following-sibling::*[1])='milestone' and following-sibling::*[1]/@ana=('hc:ZoneBeginning', 'hc:ZoneShift')))
        and
        (name(preceding-sibling::*[1])=('lb', 'cb', 'pb') 
        or (name(preceding-sibling::*[1])='milestone' and preceding-sibling::*[1]/@ana=('hc:ZoneBeginning', 'hc:ZoneShift')))
        ">
        <!--<xsl:value-of select="replace(replace(.,'\s+$',''), '^\s+','')" />-->
        <xsl:value-of select="replace(.,'\s+$','') => replace('^\s+','')" />
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="."/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  
  

</xsl:stylesheet>
