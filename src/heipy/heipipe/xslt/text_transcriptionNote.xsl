<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs"    
     version="3.0" xpath-default-namespace="http://www.tei-c.org/ns/1.0"
     xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
    xmlns:hc="https://lod.ub.uni-heidelberg.de/ontologies/heieditions/hc/current/"
    >
    
    <xsl:output method="xml"></xsl:output>

    <!-- Identity template -->
    <xsl:mode on-no-match="shallow-copy" />
    
    <xsl:template match="note[not(@*)]">
        <xsl:copy>
            <xsl:attribute name="ana">hc:TranscriptionNote</xsl:attribute>
            <xsl:copy-of select="node()"/>
        </xsl:copy>
    </xsl:template>
    
    
</xsl:stylesheet>