<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="3.0" xpath-default-namespace="http://www.tei-c.org/ns/1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

    <xsl:mode on-no-match="shallow-copy"/>

    <xsl:template match="publicationStmt">
        <xsl:choose>
            <xsl:when test="not(publisher[@xml:id = 'ub_heidelberg'])">
                <xsl:message terminate="yes">ERROR:Mandatory publisher[@xml:id = 'ub_heidelberg'] in publicationStmt is missing!</xsl:message>
            </xsl:when>
            <xsl:when test="not(pubPlace)">
                <xsl:message terminate="yes">ERROR:Mandatory pubPlace in publicationStmt is missing!</xsl:message>
            </xsl:when>
            <xsl:when test="not(date[@when])">
                <xsl:message terminate="yes">ERROR:Mandatory date[@when] in publicationStmt is missing!</xsl:message>
            </xsl:when>
            <xsl:when test="not(availability[licence])">
                <xsl:message terminate="yes">ERROR:Mandatory availability[licence] in publicationStmt is missing!</xsl:message>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy>
                    <xsl:apply-templates/>
                </xsl:copy>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>
