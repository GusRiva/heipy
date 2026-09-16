<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
    version="3.0"
    xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns="http://www.tei-c.org/ns/1.0">
    
    <xsl:output method="xml"/>
    
    <xsl:mode on-no-match="shallow-copy" />
    
    <xsl:template match="pb[@facs][not(@xml:id)]">
        <xsl:copy>
            <xsl:copy-of select="@*"/>
            <xsl:attribute name="xml:id" select="'pb__' || replace(@facs, '#','')"/>            
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>
