<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
    version="3.0"
    xpath-default-namespace="http://www.tei-c.org/ns/1.0"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    
    >
    
    <xsl:output method="xml"/>
    <xsl:mode on-no-match="shallow-copy" use-accumulators="cb-count pb-cb-count"/>
    
    <!-- Accumulator to count cb + Zone milestones -->
    <xsl:accumulator name="cb-count" as="xs:integer" initial-value="0">
        <xsl:accumulator-rule match="cb | milestone[contains(@ana, 'hc:Zone')]" select="$value + 1"/>
    </xsl:accumulator>
    
    <!-- Accumulator to track cb count *at* previous pb -->
    <xsl:accumulator name="pb-cb-count" as="xs:integer" initial-value="0">
        <xsl:accumulator-rule match="pb" select="accumulator-before('cb-count') + 1"/>
    </xsl:accumulator>
    
    <!-- Template for cb and milestone -->
    <xsl:template match="cb | milestone[contains(@ana, 'hc:Zone')]">
        <xsl:variable name="cb_before" select="accumulator-before('cb-count')"/>
        <xsl:variable name="cb_at_pb" select="accumulator-before('pb-cb-count')"/>
        
        <xsl:variable name="new_rendition">
            <xsl:value-of select="@rendition"/>
            <xsl:if test="$cb_before = $cb_at_pb">
                <xsl:text> hc:Suppress</xsl:text>
            </xsl:if>
        </xsl:variable>
        
        <xsl:copy>
            <xsl:if test="normalize-space($new_rendition) != ''">
                <xsl:attribute name="rendition" select="normalize-space($new_rendition)"/>
            </xsl:if>
            <!-- For testing puposes here:-->
            <!--<xsl:attribute name="rendition">
                <xsl:value-of select="$cb_before"/>
                <xsl:text> </xsl:text>
                <xsl:value-of select="$cb_at_pb"/>
            </xsl:attribute>-->
            <xsl:apply-templates select="node() | @* except @rendition"/>
        </xsl:copy>
    </xsl:template>
    
    
</xsl:stylesheet>
