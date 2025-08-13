<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs"    
    version="3.0" xpath-default-namespace="http://www.tei-c.org/ns/1.0"
    xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
    >
    
    <xsl:output method="xml"></xsl:output>
    
    <xsl:param name="note_classes"></xsl:param>
    <xsl:variable name="note_classes_tok" as="xs:string*" 
        select="tokenize($note_classes, '\s+')" />
    
    <!-- Identity template -->
    <xsl:mode on-no-match="shallow-copy" />
    
    <xsl:template match="
        note[
            not(contains-token(@ana, 'hc:EditorialContent'))
            and
            tokenize(@ana, '\s+') = $note_classes_tok
        ]
        ">
        <xsl:copy>
            <xsl:copy-of select="@*"></xsl:copy-of>
            <xsl:attribute name="ana" select="@ana ||  ' hc:EditorialContent'"></xsl:attribute>
            <xsl:copy-of select="node()"></xsl:copy-of>
        </xsl:copy>
    </xsl:template>
    
    
</xsl:stylesheet>