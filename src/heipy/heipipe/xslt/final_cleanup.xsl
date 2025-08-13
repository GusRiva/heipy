<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  >

<!-- 
    aim:
        Everything we want to remove at the veryend
    author: 
        Gustavo Fernández Riva
-->  
     
  <xsl:output method="xml"/>

  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />
  
  <xsl:template match="standOff">
  </xsl:template>
  
</xsl:stylesheet>
