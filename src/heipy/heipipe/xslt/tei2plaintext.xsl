<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
    xmlns:tei="http://www.tei-c.org/ns/1.0" exclude-result-prefixes="#all" version="3.0">

    <!-- Output plain text -->

    <xsl:mode on-no-match="shallow-skip"/>

    <xsl:output method="text"/>

    <!--  boolean parameter to indicate whether to mark deleted and substituted text, or to leave substituted text unmarked while omitting deleted text from the output-->
    <xsl:param name="markSubst" as="xs:boolean" select="true()"/>

    <!-- A parameter to control the treatment of abbreviations, allowing the options 'keep' to retain abbreviations or 'resolve' to display expanded text. -->
    <xsl:param name="abbr" as="xs:string" select="'keep'"/>

    <!-- Specify either 'reg' to display normalized text or 'orig' to display original text.-->
    <xsl:param name="textDisplayMode" as="xs:string" select="'orig'"/>

    <!-- For 'sic' or 'corrected' text display, use the parameter 'corr' to show corrected text or 'sic' to show original text, which will be appropriately marked. -->
    <xsl:param name="correctionDisplayMode" as="xs:string" select="'sic'"/>

    <!-- Keep or remove forme worke -->
    <xsl:param name="fw" as="xs:string" select="'keep'"/>

    <!-- Specify either 'structural' or 'semantic" to set line breaks at the corresponding positions -->
    <xsl:param name="lineBreaks" as="xs:string" select="'structural'"/>

    <!-- Show text additions supplied by the editor. Default value is false, which hides these additions -->
    <xsl:param name="showSupplied" as="xs:boolean" select="false()"/>

    <!-- Parameter to determine whether to mark surplus. Default is false, in which case text considered surplus will stay unmarked.  -->
    <xsl:param name="markSurplus" select="true()"/>

    <!-- retain all text inside of tei:text -->

    <xsl:template match="tei:text//text()">
        <xsl:value-of select="."/>
    </xsl:template>
<!--
    <xsl:template match="tei:title">
        <xsl:sequence select="'&#x7B;', ., '&#x7D;'"/>
        <xsl:text>&#10;</xsl:text>
    </xsl:template>
-->
    <xsl:template match="tei:lb">
        <xsl:choose>
            <xsl:when test="$lineBreaks = 'structural'">
                <xsl:text>&#10;</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:choose>
                    <xsl:when test="./@break='no'"/>
                    <xsl:otherwise>
                        <xsl:value-of select="'&#32;'"/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="tei:p">
        <xsl:if test="count(preceding::tei:p) > 0 and ($lineBreaks = 'semantic')">
            <xsl:text>&#10;</xsl:text>
        </xsl:if>
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="tei:l">
        <xsl:if test="count(preceding::tei:l) > 0 and ($lineBreaks = 'semantic')">
            <xsl:text>&#10;</xsl:text>
        </xsl:if>
        <xsl:apply-templates/>
    </xsl:template>

    <!-- Editorial notes out -->

    <xsl:template match="tei:note | tei:figDesc | tei:metamark"/>

    <!-- Rules for handling text content based on which parameter values are passed -->

    <xsl:template match="tei:del">
        <xsl:if test="($markSubst = true() and self::tei:del)">
            <xsl:sequence select="'&#x301A;', ., '&#x301B;'"/>
        </xsl:if>
    </xsl:template>

    <xsl:template match="tei:add">
        <xsl:choose>
            <xsl:when test="($markSubst = true())">
                <xsl:copy-of select="'&#x5C;', ., '&#x2F;'"/>
            </xsl:when>
            <xsl:when test="($markSubst = false())">
                <xsl:apply-templates/>
            </xsl:when>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="tei:choice/tei:abbr | tei:choice/tei:expan">
        <xsl:choose>
            <xsl:when
                test="($abbr = 'keep' and self::tei:abbr) or ($abbr = 'resolve' and self::tei:expan)">
                <xsl:apply-templates/>
            </xsl:when>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="tei:choice/tei:am | tei:choice/tei:ex">
        <xsl:choose>
            <xsl:when
                test="($abbr = 'keep' and self::tei:am) or ($abbr = 'resolve' and self::tei:ex)">
                <xsl:apply-templates/>
            </xsl:when>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="tei:choice/tei:orig | tei:choice/tei:reg">
        <xsl:choose>
            <xsl:when test="($textDisplayMode = 'reg' and self::tei:reg)">
                <xsl:copy-of select="."/>
            </xsl:when>
            <xsl:when test="($textDisplayMode = 'orig' and self::tei:orig)">
                <xsl:copy-of select="."/>
            </xsl:when>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="tei:choice/tei:sic | tei:choice/tei:corr">
        <xsl:choose>
            <xsl:when test="($correctionDisplayMode = 'corr' and self::tei:corr)">
                <xsl:copy-of select="."/>
            </xsl:when>
            <xsl:when test="($correctionDisplayMode = 'sic' and self::tei:sic)">
                <xsl:copy-of select="concat(., '(sic!)')"/>
            </xsl:when>
        </xsl:choose>
    </xsl:template>

    <!-- mark unclear -->

    <xsl:template match="tei:unclear">
        <xsl:analyze-string select="." regex="[A-Za-z]">
            <xsl:matching-substring>
                <xsl:value-of select="concat(., '&#x0323;')"/>
            </xsl:matching-substring>
            <xsl:non-matching-substring>
                <xsl:value-of select="."/>
            </xsl:non-matching-substring>
        </xsl:analyze-string>
    </xsl:template>

    <!-- representation for tei:space, if tei:space has no further information insert single whitespace character-->

    <xsl:template match="tei:space">
        <xsl:variable name="spaces" select="'&#32;'"/>
        <xsl:choose>
            <xsl:when test="@quantity">

                <xsl:value-of select="
                        string-join((for $i in 1 to xs:integer(@quantity)
                        return
                            $spaces), '')"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="'&#32;'"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="tei:gap">
        <xsl:value-of select="'&#x5B;&#8230;&#x5D;'"/>
    </xsl:template>

    <xsl:template match="tei:fw">
        <xsl:choose>
            <xsl:when test="$fw = 'keep'">
                <xsl:value-of select="."/>
            </xsl:when>
            <xsl:when test="$fw = 'remove'"/>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="tei:supplied">
        <xsl:choose>
            <xsl:when test="$showSupplied = true()">
                <xsl:sequence select="'&#x2329;', ., '&#x232A;'"/>
            </xsl:when>
            <xsl:otherwise/>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="tei:surplus">
        <xsl:choose>
            <xsl:when test="$markSurplus = true()">
                <xsl:sequence select="'&#x7B;', ., '&#x7D;'"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="tei:milestone[@ana = 'hc:EditorialDeletionSpan']">
        <xsl:choose>
            <xsl:when
                test="$markSurplus = true() and @spanTo/substring-after(., '#') = following::tei:anchor/@xml:id">
                <xsl:sequence select="'&#x5B;'"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="tei:milestone[@ana = 'hc:EditorialAdditionSpan']">
        <xsl:choose>
            <xsl:when
                test="$showSupplied = true() and @spanTo/substring-after(., '#') = following::tei:anchor/@xml:id">
                <xsl:sequence select="'&#x2329;'"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="tei:delSpan">
        <xsl:choose>
            <xsl:when
                test="$markSubst = true() and @spanTo/substring-after(., '#') = following::tei:anchor/@xml:id">
                <xsl:sequence select="'&#x301A;'"/>
            </xsl:when>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="tei:addSpan">
        <xsl:choose>
            <xsl:when
                test="$markSubst = true() and @spanTo/substring-after(., '#') = following::tei:anchor/@xml:id">
                <xsl:sequence select="'&#x5C;&#32;'"/>
            </xsl:when>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="tei:anchor">
        <xsl:choose>
            <xsl:when
                test="$showSupplied = true() and @xml:id = preceding::tei:milestone[@ana = 'hc:EditorialAdditionSpan']/@spanTo/substring-after(., '#')">
                <xsl:sequence select="'&#x232A;'"/>
            </xsl:when>
            <xsl:when
                test="$markSurplus = true() and @xml:id = preceding::tei:milestone[@ana = 'hc:EditorialDeletionSpan']/@spanTo/substring-after(., '#')">
                <xsl:sequence select="'&#x5D;'"/>
            </xsl:when>
            <xsl:when
                test="$markSubst = true() and @xml:id = preceding::tei:delSpan/@spanTo/substring-after(., '#')">
                <xsl:sequence select="'&#x301B;'"/>
            </xsl:when>
            <xsl:when
                test="$markSubst = true() and @xml:id = preceding::tei:addSpan/@spanTo/substring-after(., '#')">
                <xsl:sequence select="'&#32;&#x2F;'"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:apply-templates/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>
