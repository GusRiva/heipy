<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs"    
     version="3.0" xpath-default-namespace="http://www.tei-c.org/ns/1.0"
     xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
     xmlns:tei="http://www.tei-c.org/ns/1.0"
    >
    
    <xsl:output method="xml"></xsl:output>
    
    <xsl:param name="delenda_name">zone</xsl:param>
    <xsl:param name="delenda_attr_name">ana</xsl:param>
    <xsl:param name="delenda_attr_val">hc:LineZone</xsl:param>
    
    <!-- Identity template -->
    <xsl:mode on-no-match="shallow-copy" />
    
    <xsl:template match="*[name() = $delenda_name][@*[name() = $delenda_attr_name]= $delenda_attr_val]">
        <xsl:apply-templates select="node()"/>
    </xsl:template>
    
    
</xsl:stylesheet>