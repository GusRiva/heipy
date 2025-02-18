<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  >

<!-- 
    aim:
          making explicit to which zone every single line belongs 
          
    logic: 
          - for every <lb> look for the first preceding <cb>|<milestone ana="hc:ZoneBeginning">|<milestone ana="hc:ZoneShift"
          - copy the @facs of such a <cb>... into @hei:belongsToZone on the current <lb>
          
-->  
     
  <xsl:output method="xml"/>

  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />

  <xsl:template match="lb | milestone[tokenize(@ana, '\s+') = 'hc:LineSegmentBeginning']" priority="1">
    <xsl:copy>
      <xsl:copy-of select="@*"></xsl:copy-of>
      <xsl:attribute 
        name="belongsToZone" 
        namespace="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
        select="preceding::*[name() = 'cb' or (name() = 'milestone' and (tokenize(@ana, '\s+') = 'hc:ZoneBeginning' or tokenize(@ana, '\s+') = 'hc:ZoneShift'))][1]/@facs"
        ></xsl:attribute>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="lb[@facs]" priority="5">
    <xsl:variable name="facs" select="@facs"/>
    <xsl:copy>
      <xsl:copy-of select="@*"/>
      <xsl:attribute 
        name="belongsToZone" 
        namespace="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
        >
        <xsl:text>#</xsl:text>
        <xsl:value-of select="//zone[@xml:id=substring-after( $facs, '#')]/ancestor::zone[ tokenize(@ana,'\s+') = 'hc:TextZone']/@xml:id"/>
      </xsl:attribute>
    </xsl:copy>
  </xsl:template>
   
  <!-- lb is within some ancestor with @facs -->
  <xsl:template match="lb[ancestor::*[@facs]] | milestone[tokenize(@ana, '\s+') = 'hc:LineSegmentBeginning'][ancestor::*[@facs]]"
      priority="4">
    <xsl:copy>
      <xsl:copy-of select="@*"></xsl:copy-of>
      <xsl:attribute 
        name="belongsToZone" 
        namespace="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
        select="ancestor::*[@facs][1]/@facs"
        ></xsl:attribute>
    </xsl:copy>
  </xsl:template>
  
  <!-- @hei:includedInZone is deprecated - this code should be removed as soon as it is used by no project-->  
  <xsl:template match="lb[ancestor::*[@hei:includedInZone]] | milestone[tokenize(@ana, '\s+') = 'hc:LineSegmentBeginning'][ancestor::*[@hei:includedInZone]]" 
    priority="3">
    <xsl:copy>
      <xsl:copy-of select="@*"></xsl:copy-of>
      <xsl:attribute 
        name="belongsToZone" 
        namespace="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
        select="ancestor::*[@hei:includedInZone][1]/@hei:includedInZone"
        ></xsl:attribute>
    </xsl:copy>
  </xsl:template>
  
  
</xsl:stylesheet>
