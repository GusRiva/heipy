<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs"    
    version="3.0" xpath-default-namespace="http://www.tei-c.org/ns/1.0">
    
    <xsl:output method="xml"></xsl:output>
    
    <!-- Identity template -->
    <xsl:mode on-no-match="shallow-copy" />
    
    <!-- 
        The following code has been adapted from 
        https://wiki.tei-c.org/index.php/XML_Whitespace 
    -->
    
    <xsl:template match="text()[ancestor::text]" priority="1">
        <xsl:choose>
            <xsl:when
                test="ancestor::*[@xml:space][1]/@xml:space='preserve'">
                <xsl:value-of select="."/>
            </xsl:when>
            <xsl:otherwise>
                <!-- Cache frequently used values -->
                <xsl:variable name="normalized" select="normalize-space(.)"/>
                <xsl:variable name="has-preceding" select="exists(preceding-sibling::node())"/>
                <xsl:variable name="has-following" select="exists(following-sibling::node())"/>
                <xsl:variable name="first-char" select="substring(., 1, 1)"/>
                <xsl:variable name="last-char" select="substring(., string-length(.))"/>

                <!-- Retain one leading space if node isn't first, has non-space content, and has leading space -->
                <xsl:if test="$has-preceding and normalize-space($first-char)='' and $normalized!=''">
                    <xsl:text> </xsl:text>
                </xsl:if>
                <xsl:value-of select="$normalized"/>
                <xsl:choose>
                    <!-- node is an only child, and has content but it's all space -->
                    <xsl:when test="not($has-preceding) and not($has-following) and string-length()!=0 and $normalized=''">
                        <xsl:text> </xsl:text>
                    </xsl:when>
                    <!-- JS: beim vorangehenden Fall sollte noch genauer geprüft werden,
                        ob es sich nicht um ein spezielles Leerzeichen handelt,
                        das bewahrt werden sollte, wahrscheinlich aber nur innerhalb von <c>;
                        Selbstkorrektur: Das ist wahrscheinlich nicht nötig, weil normalize-space() spezielle Leerzeichen
                        nicht als whitespace behandelt
                    -->
                    <!-- node isn't last, isn't first, and has trailing space -->
                    <xsl:when test="$has-preceding and $has-following and normalize-space($last-char)=''">
                        <xsl:text> </xsl:text>
                    </xsl:when>
                    <!-- node isn't last, is first, has trailing space, and has non-space content   -->
                    <!-- JS: folgende Bedingung ursprünglich:
                    test="position()=1 and matches(.,'\s$') and normalize-space()!=''"
                    -->
                    <xsl:when test="not($has-preceding) and $has-following and normalize-space($last-char)='' and $normalized!=''">
                        <xsl:text> </xsl:text>
                    </xsl:when>
                </xsl:choose>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    

    
</xsl:stylesheet>