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
                <!--<xsl:variable name="attributes" select="count(parent::element()/@*)"/>-->
                <!-- Retain one leading space if node isn't first, has
         non-space content, and has leading space.-->
                <xsl:if test="preceding-sibling::node()  and          matches(.,'^\s') and          normalize-space()!=''">
                    <xsl:text> </xsl:text>
                </xsl:if>
                <xsl:value-of select="normalize-space(.)"/>
                <xsl:choose>
                    <!-- node is an only child, and has content but it's all space -->
                    <xsl:when test="not(preceding-sibling::node()) and not(following-sibling::node()) and string-length()!=0 and      normalize-space()=''">
                        <xsl:text> </xsl:text>
                    </xsl:when>
                    <!-- JS: beim vorangehenden Fall sollte noch genauer geprüft werden, 
                        ob es sich nicht um ein spezielles Leerzeichen handelt,
                        das bewahrt werden sollte, wahrscheinlich aber nur innerhalb von <c>;
                        Selbstkorrektur: Das ist wahrscheinlich nicht nötig, weil normalize-space() spezielle Leerzeichen
                        nicht als whitespace behandelt
                    -->                    
                    <!-- node isn't last, isn't first, and has trailing space -->
                    <xsl:when test="preceding-sibling::node() and position()!=last() and matches(.,'\s$')">
                        <xsl:text> </xsl:text>
                    </xsl:when>
                    <!-- node isn't last, is first, has trailing space, and has non-space content   -->
                    <!-- JS: folgende Bedingung ursprünglich:
                    test="position()=1 and matches(.,'\s$') and normalize-space()!=''"
                    -->
                    <xsl:when test="not(preceding-sibling::node()) and position()!=last() and matches(.,'\s$') and normalize-space()!=''">
                        <xsl:text> </xsl:text>
                    </xsl:when>
                </xsl:choose>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    

    
</xsl:stylesheet>