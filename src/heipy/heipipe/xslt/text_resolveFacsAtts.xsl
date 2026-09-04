<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0"
  xmlns="http://www.tei-c.org/ns/1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
>

<!--
    aim:
          convert container elements that carry a @facs attribute into the
          milestone-based zone-reference pattern expected by the SourceDoc pipeline

    logic:
          for every non-milestone element (i.e. not pb, cb, lb, milestone) with @facs:
            1. emit <milestone ana="hc:ZoneBeginning" facs="{@facs}"/> before the element
            2. emit the element itself without @facs (children recursively transformed)
            3. emit <milestone ana="hc:ZoneShift" facs="{$prev_zone_facs}"/> after the element,
               where $prev_zone_facs is taken from the nearest preceding cb, zone milestone,
               or <lb> with @facs; if no such preceding element exists, the ZoneShift is omitted

               a preceding <lb>'s own @facs points to a LineZone rather than directly to the
               TextZone/ImageZone/etc. that @facs on a ZoneShift milestone needs, so it is
               resolved to its enclosing zone the same way the lb[@facs] template in
               text_connectLbWithZone.xsl does
-->

  <xsl:output method="xml"/>
  <xsl:mode on-no-match="shallow-copy"/>

  <xsl:template match="*[@facs][not(self::milestone or self::pb or self::cb or self::lb)]">
    <xsl:variable name="prev_marker"
      select="preceding::*[self::cb
        or self::lb[@facs]
        or (self::milestone and tokenize(@ana,'\s+') = ('hc:ZoneBeginning','hc:ZoneShift'))
      ][1]"/>

    <xsl:variable name="prev_zone_facs">
      <xsl:choose>
        <xsl:when test="$prev_marker/self::lb">
          <!-- [1]: nur die naechste (innerste) passende Zone waehlen; bei verschachtelten
               Zonen (z.B. ImageZone > TextZone) wuerde value-of sonst beide xml:id mit
               Leerzeichen verketten und der belongsToZone-Wert liesse sich nicht aufloesen -->
          <xsl:variable name="enclosing_zone_id"
            select="//zone[@xml:id = substring-after($prev_marker/@facs, '#')]
              /ancestor::zone[tokenize(@ana,'\s+') = ('hc:TextZone','hc:ImageZone','hc:GraphicZone','hc:TableZone')][1]/@xml:id"/>
          <xsl:if test="$enclosing_zone_id">
            <xsl:value-of select="concat('#', $enclosing_zone_id)"/>
          </xsl:if>
        </xsl:when>
        <xsl:when test="$prev_marker">
          <xsl:value-of select="$prev_marker/@facs"/>
        </xsl:when>
      </xsl:choose>
    </xsl:variable>

    <!-- Zone beginning: take facs from this container -->
    <milestone ana="hc:ZoneBeginning" facs="{@facs}"/>

    <!-- The container itself, without @facs -->
    <xsl:copy>
      <xsl:copy-of select="@*[not(name()='facs')]"/>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>

    <!-- Zone shift: restore previous active zone (omit if none exists) -->
    <xsl:if test="string($prev_zone_facs) != ''">
      <milestone ana="hc:ZoneShift" facs="{$prev_zone_facs}"/>
    </xsl:if>
  </xsl:template>



</xsl:stylesheet>
