<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  >

<!-- 
    aim:
    
    CAVEAT: there must not be any other elements spreading over physical beginnings except for <hi> when this script is run  
    (TODO: implement this in Schematron)
    CAVEAT: The script does not work recursively for nested <hi> elements which share a <lb> deeper in their hierarchy;
          however, it resolves such cases correctly when run repeatedly. An XProc pipeline could therefore encapsulate
          e.g. five repetitions of this transformation into a single step, just to be sure. A Schematron rule could check that there are no 
          nested <hi> elements with a <lb> deeper than five levels
-->  
     
  <xsl:output method="xml" indent="no"/>

  <!-- Identity -->
  <xsl:mode on-no-match="shallow-copy" />
  
  <xsl:template match="w[lb]">
    <xsl:variable name="atts" select="@*[not(local-name() = 'id')]"/>
    <xsl:variable name="id" select="@xml:id"/>    
    <xsl:for-each-group select="node()" group-adjacent="boolean(local-name() = ('pb', 'cb', 'lb') or (local-name() = 'milestone' and tokenize(@ana, '\s+') = ('hc:ZoneBeginning', 'hc:ZoneShift')) or self::text()[normalize-space() = ''])">
      <xsl:choose>
        <xsl:when test="current-grouping-key()">
          <xsl:apply-templates select="current-group()"></xsl:apply-templates>
        </xsl:when>
        <xsl:otherwise>
          <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:copy-of select="$atts"></xsl:copy-of>
            <xsl:if test="$id != ''">
              <xsl:choose>
                <xsl:when test="position() = 1">
                  <xsl:attribute name="xml:id" select="$id"></xsl:attribute>     
                </xsl:when>
                <xsl:when test="position() != 1">
                  <xsl:attribute name="xml:id" select="$id || '-' || position() - 1"></xsl:attribute>                                
                </xsl:when>
              </xsl:choose>
            </xsl:if>            
            <xsl:choose>
              <xsl:when test="position() = 1">
                <xsl:attribute name="part" select="'I'"></xsl:attribute>
              </xsl:when>
              <xsl:when test="position() = last()">
                <xsl:attribute name="part" select="'F'"></xsl:attribute>
              </xsl:when>
              <xsl:otherwise>
                <xsl:attribute name="part" select="'M'"></xsl:attribute>               
              </xsl:otherwise>
            </xsl:choose>
            <xsl:apply-templates select="current-group()"></xsl:apply-templates>
          </xsl:element>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each-group>
  </xsl:template>
  
  <xsl:template match="w[milestone[tokenize(@ana, '\s+') = 'hc:LineSegmentBeginning']]">
    <xsl:variable name="atts" select="@*[not(local-name() = 'id')]"/>
    <xsl:variable name="id" select="@xml:id"/>    
    <xsl:for-each-group select="node()" group-adjacent="boolean(local-name() = 'milestone' and tokenize(@ana, '\s+') = 'hc:LineSegmentBeginning')">
      <xsl:choose>
        <xsl:when test="current-grouping-key()">
          <xsl:copy-of select="current-group()"></xsl:copy-of>
        </xsl:when>
        <xsl:otherwise>
          <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:copy-of select="$atts"></xsl:copy-of>
            <xsl:if test="$id != ''">
              <xsl:choose>
                <xsl:when test="position() = 1">
                  <xsl:attribute name="xml:id" select="$id"></xsl:attribute>     
                </xsl:when>
                <xsl:when test="position() != 1">
                  <xsl:attribute name="xml:id" select="$id || '-' || position() - 1"></xsl:attribute>                                
                </xsl:when>
              </xsl:choose>
            </xsl:if>            
            <xsl:choose>
              <xsl:when test="position() = 1">
                <xsl:attribute name="part" select="'I'"></xsl:attribute>
              </xsl:when>
              <xsl:when test="position() = last()">
                <xsl:attribute name="part" select="'F'"></xsl:attribute>
              </xsl:when>
              <xsl:otherwise>
                <xsl:attribute name="part" select="'M'"></xsl:attribute>               
              </xsl:otherwise>
            </xsl:choose>
            <xsl:apply-templates select="current-group()"></xsl:apply-templates>
          </xsl:element>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each-group>
  </xsl:template>
  
</xsl:stylesheet>
