<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs"
     version="3.0" xpath-default-namespace="http://www.tei-c.org/ns/1.0"
     xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
    >

<!--    Removes the initial zones and facs attribute.
        Should be replaced with the actual way to handle initials
        -->

    <xsl:output method="xml"/>

    <!-- Identity template -->
    <xsl:mode on-no-match="shallow-copy" />

    <xsl:template match="hei:initial">
        <xsl:copy>
            <xsl:apply-templates select="node()|@*[name() != 'facs']"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="zone[@ana='hc:InitialZone']"/>


</xsl:stylesheet>