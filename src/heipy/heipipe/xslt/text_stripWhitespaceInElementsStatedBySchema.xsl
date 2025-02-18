<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs"    
    version="3.0" xpath-default-namespace="http://www.tei-c.org/ns/1.0">
    
    <!-- 
        aim: remove "whitespace only" text nodes which are children of elements where "real" text nodes are not allowed 
            and "whitespace only" text nodes are therefore considered insignificant
    -->
    
    <xsl:output method="xml"></xsl:output>
    
    <!-- Identity template -->
    <xsl:mode on-no-match="shallow-copy" />

    <xsl:variable name="stripElements"
    select="tokenize(document('hei_stripspace.xsl')/xsl:strip-space/@elements, '\s+')"
    as="xs:string*" />
    
    <xsl:template match="text()[normalize-space() = ''][name(parent::element()) = $stripElements]">
    </xsl:template>
    
</xsl:stylesheet>
