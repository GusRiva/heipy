<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="3.0" xmlns:eg="http://www.tei-c.org/ns/Examples" xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
    xmlns:xi="http://www.w3.org/2001/XInclude" xmlns:fn="http://www.w3.org/2005/xpath-functions" xmlns="http://www.tei-c.org/ns/1.0" xpath-default-namespace="http://www.tei-c.org/ns/1.0">

    <xsl:output method="xml"/>

    <xsl:mode on-no-match="shallow-copy"/>

    <xsl:template match="ptr[tokenize(@ana, '\s+') = ('hc:URLReference', 'hc:ExternalLink', 'hc:InternalLink', 'hc:IIIFManifestURL')]">
        <xsl:element name="ref" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:copy-of select="@*"></xsl:copy-of> 
            <xsl:value-of select="@target"/>
        </xsl:element>
    </xsl:template>

</xsl:stylesheet>
