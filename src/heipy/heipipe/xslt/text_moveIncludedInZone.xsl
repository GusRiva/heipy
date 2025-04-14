<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  >

<!-- 
    aim:
          moving elements with @facs to the end of <text> and removing the attribute;
          the same processing is applied to children of figure[@facs] marked as hc:FigureText
          
    author: Jakub Šimek
          
-->  
     
  <xsl:output method="xml"/>

  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />
  
  <xsl:variable name="included" select="//*[not(local-name() = ('pb','cb','lb','milestone','figure'))][@hei:includedInZone or @facs]|//*[tokenize(@ana, '\s+') = 'hc:FigureText'][parent::figure[@facs]]" as="item()*"/>
  <!-- @hei:includedInZone is deprecated and should be removed from the script as soon as all editions are migrated to using @facs -->
  
  <xsl:template match="text">
    <xsl:copy>
      <xsl:copy-of select="@*"></xsl:copy-of>
      <xsl:apply-templates></xsl:apply-templates>
      
    </xsl:copy>
    <xsl:for-each select="$included">
      <xsl:copy>
        <xsl:copy-of select="@*[not(local-name() = ('includedInZone','facs'))]"></xsl:copy-of>
        <xsl:copy-of select="node()"></xsl:copy-of>
      </xsl:copy>
    </xsl:for-each>
  </xsl:template>
 
  <!-- remove the elements with @hei:includedInZone or @facs from the text -->   
  <xsl:template match="*[not(local-name() = ('pb','cb','lb','milestone','figure'))][@hei:includedInZone or @facs]|//*[tokenize(@ana, '\s+') = 'hc:FigureText'][parent::figure[@facs]]"></xsl:template>
  
 
  
</xsl:stylesheet>
