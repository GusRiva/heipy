<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs"    
    version="3.0" xpath-default-namespace="http://www.tei-c.org/ns/1.0"
    xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
    >
    
    <xsl:output method="xml"></xsl:output>
    
    <!-- Identity template -->
    <xsl:mode on-no-match="shallow-copy" />
    
    <xsl:variable name="tokenizedElements" select="tokenize(/TEI/teiHeader/encodingDesc/hei:elementsWithTokenizedContent/@include)" as="item()*"/>       
    <xsl:template match="text()
        [ancestor::text]
        [(ancestor::*!local-name()) = $tokenizedElements]
        [normalize-space() = '']
        [not(parent::c)]
        "></xsl:template>
    
</xsl:stylesheet>