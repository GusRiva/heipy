<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  >

<!-- 
    aim:
          making explicit to which line every single line segment belongs if it is not stated already
          
    logic: 
          - for every <milestone> with type hc:LineSegmentBeginning which does not have @hei:belongsToLine already look for the first preceding <lb>
          - copy the @n of such a <lb>... into @hei:belongsToLine on the current <milestone>
          
-->  
     
  <xsl:output method="xml"/>

  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />
  
  <xsl:template match="milestone[tokenize(@ana, '\s+') = 'hc:LineSegmentBeginning'][not(@hei:belongsToLine)]">
    <xsl:copy>
      <xsl:copy-of select="@*"></xsl:copy-of>
      <xsl:attribute 
        name="belongsToLine" 
        namespace="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
        select="preceding::lb[1]/@n"
        ></xsl:attribute>
    </xsl:copy>
  </xsl:template>
  
 
  
</xsl:stylesheet>
