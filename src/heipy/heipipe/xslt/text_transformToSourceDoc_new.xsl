<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.tei-c.org/ns/1.0">

  <xsl:output method="xml"/>
  
  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />
  
  <xsl:template match="/TEI">
    <xsl:copy>
      <xsl:copy-of select="@*"></xsl:copy-of>
      <xsl:copy-of select="/TEI/teiHeader"></xsl:copy-of>
      <xsl:element name="sourceDoc" namespace="http://www.tei-c.org/ns/1.0">
        <xsl:apply-templates select="/TEI/facsimile" mode="facsimile_to_sourceDoc"></xsl:apply-templates>
      </xsl:element>
    </xsl:copy>    
  </xsl:template>
  
  <xsl:template match="facsimile" mode="facsimile_to_sourceDoc">
    <!-- the content of <facsimile> should from now on be transformed inside of <sourceDoc> -->
    <xsl:apply-templates></xsl:apply-templates>
  </xsl:template>
  
  <xsl:template match="zone">
    <xsl:variable name="zone_id" select="@xml:id"/>
    <xsl:copy>  
        <!-- copy itself as element and copy all its attributes: -->
        <xsl:copy-of select="@*"></xsl:copy-of>
        <!-- copy the description of the zone, if present: -->
        <xsl:copy-of select="desc"></xsl:copy-of>
        <xsl:choose>
          <!-- if the <zone> contains other <zone>s (i.e. if it serves as container in the layout declaration): -->
          <xsl:when test="zone">
            <xsl:apply-templates/>
          </xsl:when>
          <!-- if the zone does not contain other <zone>s (i.e. it shoud now be filled with content from <text>): -->
         
          <xsl:when test="tokenize(@ana, '\s+') = 'hc:TextZone'">
              <!-- for each <lb> connected to this <zone>: -->
              <xsl:for-each select="//lb[substring-after(@hei:belongsToZone, '#') = $zone_id]">
                <!-- sort the <lb>s according to their @n (works even with two numbers separated by dot because this is interpreted as decimal) -->
                <xsl:sort select="@n" data-type="number"></xsl:sort>
                <xsl:variable name="line_number" select="@n"/>
                <xsl:text>
                        </xsl:text>
                <xsl:element name="line" namespace="http://www.tei-c.org/ns/1.0">
                  <!-- copy all of the <lb> attributes except @hei:belongsToZone and @break: -->
                  <xsl:copy-of select="@*[not(local-name() = ('belongsToZone', 'break'))]"/>
                  <!-- set @xml:space on "preserve" -->
                  <xsl:attribute name="xml:space" select="'preserve'"/>
                  <xsl:if test="following-sibling::element()[1]/self::seg[@type = 'line']">
                    <xsl:apply-templates select="following-sibling::seg[1]/node()"></xsl:apply-templates>
                  </xsl:if>  
                  
                  <xsl:call-template name="getLineSegmentBeginning">
                    <xsl:with-param name="line_number" select="$line_number"/>
                    <xsl:with-param name="zone_id" select="$zone_id"/>
                  </xsl:call-template>
                  
                </xsl:element>
              </xsl:for-each>
                  
              <!-- handling cases where there are no lines in a text zone but an editorial gap (and possibly also some milestones): -->
              <xsl:if test="//cb[substring-after(@facs, '#') = $zone_id]/following-sibling::element()[1]/self::seg[@type = 'zone']
                or
                //milestone[tokenize(@ana, '\s+') = 'hc:ZoneBeginning'][substring-after(@facs, '#') = $zone_id]/following-sibling::element()[1]/self::seg[@type = 'zone']
                ">
                <xsl:apply-templates select="//cb[substring-after(@facs, '#') = $zone_id]/following-sibling::seg[1]/node()
                  |
                  //milestone[tokenize(@ana, '\s+') = 'hc:ZoneBeginning'][substring-after(@facs, '#') = $zone_id]/following-sibling::seg[1]/node()
                  "></xsl:apply-templates>
              </xsl:if>                
          </xsl:when>
          
          <xsl:when test="tokenize(@ana, '\s+') = 'hc:LineZone'">
            <xsl:variable name="text_zone_id" select="ancestor::zone[tokenize(@ana, '\s+') = 'hc:TextZone']/@xml:id"/>
            <xsl:variable name="corresp_lb" select="//lb[substring-after(@facs, '#') = $zone_id]"/>
            <xsl:variable name="line_number" select="$corresp_lb/@n"/>
            <xsl:element name="line" namespace="http://www.tei-c.org/ns/1.0">
              <xsl:copy-of select="@n"/>
              <xsl:if test="not(@n)">
                <xsl:attribute name="n" select="$line_number"/>
              </xsl:if>
              <!-- set @xml:space on "preserve" -->
              <xsl:attribute name="xml:space" select="'preserve'"/>
              
              <xsl:if test="$corresp_lb[1]/following-sibling::element()[1]/self::seg[@type = 'line']">
                <xsl:apply-templates select="$corresp_lb[1]/following-sibling::seg[1]/node()"/>
              </xsl:if>
              
              
              <xsl:call-template name="getLineSegmentBeginning">
                <xsl:with-param name="line_number" select="$line_number"/>
                <xsl:with-param name="zone_id" select="$text_zone_id"/>
              </xsl:call-template>
              
            </xsl:element>
          </xsl:when>
          
          <xsl:when test="tokenize(@ana, '\s+') = 'hc:GapZone'">
              <xsl:apply-templates select="//cb[substring-after(@facs, '#') = $zone_id]/following-sibling::seg[1]/node()
                |
                //milestone[tokenize(@ana, '\s+') = 'hc:ZoneBeginning'][substring-after(@facs, '#') = $zone_id]/following-sibling::seg[1]/node()
                "></xsl:apply-templates>                
          </xsl:when>
          <xsl:when test="tokenize(@ana, '\s+') = 'hc:SpaceZone'">
              <xsl:apply-templates select="//cb[substring-after(@facs, '#') = $zone_id]/following-sibling::seg[1]/node()
                |
                //milestone[tokenize(@ana, '\s+') = 'hc:ZoneBeginning'][substring-after(@facs, '#') = $zone_id]/following-sibling::seg[1]/node()
                "></xsl:apply-templates>                
          </xsl:when>
          <xsl:when test="tokenize(@ana, '\s+') = ('hc:ImageZone','hc:GraphicZone')">
              <xsl:apply-templates select="//cb[substring-after(@facs, '#') = $zone_id]/following-sibling::seg[1]/node()
                |
                //milestone[tokenize(@ana, '\s+') = 'hc:ZoneBeginning'][substring-after(@facs, '#') = $zone_id]/following-sibling::seg[1]/node()
                "></xsl:apply-templates>               
          </xsl:when>
          <xsl:when test="tokenize(@ana, '\s+') = 'hc:TableZone'">
                <xsl:apply-templates select="//cb[substring-after(@facs, '#') = $zone_id]/following-sibling::seg[1]/node()
                  |
                  //milestone[tokenize(@ana, '\s+') = 'hc:ZoneBeginning'][substring-after(@facs, '#') = $zone_id]/following-sibling::seg[1]/node()
                  "></xsl:apply-templates>               
              </xsl:when>
        </xsl:choose>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template name="getLineSegmentBeginning">
    <xsl:param name="zone_id"/>
    <xsl:param name="line_number"/>
    
    <xsl:for-each select="//milestone[tokenize(@ana, '\s+') = 'hc:LineSegmentBeginning']
      [substring-after(@hei:belongsToZone, '#') = $zone_id]
      [@hei:belongsToLine = $line_number]
      ">
      <xsl:sort select="@n" data-type="number"></xsl:sort>
      <xsl:variable name="seg_ana" as="item()*">
        <xsl:for-each select="tokenize(@ana, '\s+')">
          <xsl:if test=". != 'hc:LineSegmentBeginning'">
            <xsl:value-of select="."/>
          </xsl:if>
        </xsl:for-each>
      </xsl:variable>
      <xsl:element name="seg" namespace="http://www.tei-c.org/ns/1.0">
        <xsl:attribute name="ana" select="'hc:LineSegment ' || string-join($seg_ana, ' ')"></xsl:attribute>
        <xsl:copy-of select="@*[not(local-name() = ('belongsToZone', 'belongsToLine', 'ana', 'break'))]"></xsl:copy-of>
        <xsl:apply-templates select="following-sibling::seg[1]/node()"></xsl:apply-templates>
      </xsl:element>
    </xsl:for-each>

  </xsl:template> 
  
                  
  
  <!-- remove the original <facsimile> -->
  <xsl:template match="facsimile"></xsl:template>
  
  <!-- remove the original empty markers for the beginnings of physical structures -->
  <xsl:template match="pb|cb|milestone[@ana='hc:ZoneBeginning']|milestone[@ana='hc:ZoneShift']"></xsl:template>
  <!-- TODO: verbessern! -->
  
</xsl:stylesheet>
