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
               where $prev_zone_facs is taken from the nearest preceding cb or zone milestone;
               if no such preceding element exists, the ZoneShift is omitted
-->

  <xsl:output method="xml"/>
  <xsl:mode on-no-match="shallow-copy"/>

  <xsl:template match="*[@facs][not(self::milestone or self::pb or self::cb or self::lb)]">
    <xsl:variable name="prev_zone_facs"
      select="preceding::*[self::cb
        or (self::milestone and tokenize(@ana,'\s+') = ('hc:ZoneBeginning','hc:ZoneShift'))
      ][1]/@facs"/>

    <!-- Zone beginning: take facs from this container -->
    <milestone ana="hc:ZoneBeginning" facs="{@facs}"/>

    <!-- The container itself, without @facs -->
    <xsl:copy>
      <xsl:copy-of select="@*[not(name()='facs')]"/>
      <xsl:apply-templates select="node()"/>
    </xsl:copy>

    <!-- Zone shift: restore previous active zone (omit if none exists) -->
    <xsl:if test="$prev_zone_facs">
      <milestone ana="hc:ZoneShift" facs="{$prev_zone_facs}"/>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
