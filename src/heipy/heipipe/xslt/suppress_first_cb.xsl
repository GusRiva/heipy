<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
    version="3.0"
    xpath-default-namespace="http://www.tei-c.org/ns/1.0"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    
    >
    
    <xsl:output method="xml"/>

    <xsl:mode on-no-match="shallow-copy" />
    
    <xsl:template match="cb | milestone[contains(@ana, 'hc:Zone')]">
        <!-- Wieviele cb oder milestone davor?        -->
        <xsl:variable name="preceding_cb" select="count(preceding::*[self::cb or self::milestone[contains(@ana, 'hc:Zone')]])" />
        <!-- Wieviele cb oder milestone vor dem letzen pb?        -->
        <xsl:variable name="preceding_cb_from_pb" select="count(preceding::pb[1]/preceding::*[self::cb or self::milestone[contains(@ana, 'hc:Zone')]])" />
        
        <xsl:variable name="new_rendition">
            <xsl:value-of select="@rendition"/>
               <!-- Genauso viele cb oder milestone vor diesem als vor dem letzen pb?           -->
            <xsl:if test="$preceding_cb = $preceding_cb_from_pb">
                <xsl:text> hc:Suppress</xsl:text>
            </xsl:if>
        </xsl:variable>
       
        <xsl:copy>
            <xsl:if test="normalize-space($new_rendition) != ''">
                <xsl:attribute name="rendition" select="normalize-space($new_rendition)"/>
            </xsl:if>
            <xsl:apply-templates select="node() | @* except @rendition"/>
        </xsl:copy>
    </xsl:template>
    
    
</xsl:stylesheet>
