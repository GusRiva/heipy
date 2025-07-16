<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  >

<!-- 
    aim:
        insert the stand-off virtual structure into the text, using milestone-anchor pairs for the container divisions
    logic:
        - resolve the container divisions ("front|body|back|div") into milestone-anchor pairs
        - group these resolved elements together with virtual headings
        - insert the content of these groups before or after the elements in the text which are referenced by the 
          special pointers, accordingly 
    author:
      Jakub Šimek
    CAVEAT:
       This script is part of the larger XProc step "text_injectStructure". It is not to be used independently.
       The result will not be valid. The new divisions will be still just milestone-anchor pairs - these
       pairs need to be transformed into real containers in the following script "text_injectStructure3.py".
-->  
     
  <xsl:output method="xml"/>

  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />
  
  <xsl:param name="structure"></xsl:param>
  
  <!-- the structure configuration to which the parameter $structure indicates the path: -->
  <xsl:variable name="structure_variable" select="doc($structure)"/>
  
  <!-- resolve the container elements "div|front|body|back" found in the structure configuration into milestone-anchor pairs: --> 
  <xsl:variable name="flattened_structure">
    <xsl:choose>
      <xsl:when test="$structure_variable/TEI/body">
        <xsl:apply-templates select="$structure_variable/TEI/body/node()" mode="structure"></xsl:apply-templates>
      </xsl:when>
      <xsl:when test="$structure_variable/TEI/text">
        <xsl:apply-templates select="$structure_variable/TEI/text/node()" mode="structure"></xsl:apply-templates>
      </xsl:when>
    </xsl:choose>
  </xsl:variable>
  
  <!-- insert separators (ad-hoc element "separator") between adjacent "anchor" and "milestone",
          i.e. at the boundary between two adjacent sibling elements (representing the boundary between two containers):
  -->
  <xsl:variable name="flattened_structure_with_separators">
    <xsl:for-each select="$flattened_structure/*">
      <xsl:choose>
        <xsl:when test="self::anchor and following-sibling::*[1]/self::milestone">
          <xsl:copy-of select="."></xsl:copy-of>
          <xsl:element name="separator" namespace="http://www.tei-c.org/ns/1.0"></xsl:element>
        </xsl:when>
        <xsl:otherwise>
          <xsl:copy-of select="."></xsl:copy-of>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
  </xsl:variable>
  
  <!-- 
    group elements between "ptr" or "separator" (i.e. sequences of "milestone", "anchor" and "head")
    into ad-hoc element "group":
  -->
  <xsl:variable name="grouped_structure">
    <xsl:for-each-group select="$flattened_structure_with_separators/node()" group-adjacent="not(self::ptr or self::separator)">
      <xsl:choose>
        <xsl:when test="current-grouping-key()">
          <xsl:element name="group" namespace="http://www.tei-c.org/ns/1.0">
            <xsl:copy-of select="current-group()"></xsl:copy-of>
          </xsl:element>
        </xsl:when>
        <xsl:otherwise>
          <xsl:copy-of select="current-group()"></xsl:copy-of>
        </xsl:otherwise>
      </xsl:choose>      
    </xsl:for-each-group>
  </xsl:variable>
  
  <!-- 
    transform the target of the pointers given in the "range()" syntax into ad-hoc @from and @to attributes:
  -->
  <xsl:variable name="grouped_structure_resolved_pointers">
    <xsl:for-each select="$grouped_structure/node()">
      <xsl:choose>
        <xsl:when test="not(self::ptr)">
          <xsl:copy-of select="."></xsl:copy-of>
        </xsl:when>
        <xsl:otherwise>
          <xsl:copy>
            <xsl:attribute name="from" select="'#' || substring-after(@target, 'wit:range(') => substring-before(')') => substring-before(',')"></xsl:attribute>
            <xsl:attribute name="to" select="'#' || substring-after(@target, 'wit:range(') => substring-before(')') => substring-after(',')"></xsl:attribute>
          </xsl:copy>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:for-each>
  </xsl:variable>
  
  <!-- templates used in "flattening" above: -->
  
  <xsl:template match="div|front|body|back" mode="structure">
    <xsl:variable name="xml_id">
      <xsl:choose>
        <xsl:when test="@xml:id">
          <xsl:value-of select="@xml:id"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:text>__</xsl:text>
          <xsl:value-of select="name()"/>
          <xsl:text>__</xsl:text>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:variable>
    <xsl:element name="milestone" namespace="http://www.tei-c.org/ns/1.0">
      <!-- ad-hoc @type used later for reconstructing the original container elements: -->
      <xsl:attribute name="type">
        <xsl:choose>
          <xsl:when test="self::div">
            <xsl:text>structure_div</xsl:text>
          </xsl:when>
          <xsl:when test="self::front">
            <xsl:text>structure_front</xsl:text>
          </xsl:when>
          <xsl:when test="self::body">
            <xsl:text>structure_body</xsl:text>
          </xsl:when>
          <xsl:when test="self::back">
            <xsl:text>structure_back</xsl:text>
          </xsl:when>
        </xsl:choose>
      </xsl:attribute>
      <xsl:copy-of select="@* except @xml"/>
      <xsl:attribute name="xml:id">
        <xsl:value-of select="$xml_id"/>
      </xsl:attribute>
    </xsl:element>
    <xsl:apply-templates mode="structure"></xsl:apply-templates>
    <xsl:element name="anchor" namespace="http://www.tei-c.org/ns/1.0">      
      <xsl:attribute name="spanFrom" select="'#' || $xml_id"></xsl:attribute>
    </xsl:element>
  </xsl:template>
  
  <xsl:template match="head|note|ptr" mode="structure">
    <xsl:copy-of select="."></xsl:copy-of>
  </xsl:template>
  
  <!-- main template inserting "flattened" structures from the configuration into the text: -->
  
  <!-- process all elements targeted by the pointers -->
  <xsl:template match="
    *[@xml:id = (for $i in $grouped_structure_resolved_pointers//ptr/@from return substring-after($i, '#'))]
    |
    *[@xml:id = (for $i in $grouped_structure_resolved_pointers//ptr/@to return substring-after($i, '#'))]">
    <xsl:choose>
      <!-- if the element is targeted by @from, i.e. it should become the first element of a virtual division: -->
      <xsl:when test="@xml:id = (for $i in $grouped_structure_resolved_pointers//ptr/@from return substring-after($i, '#'))">
        <xsl:variable name="pointer" select="$grouped_structure_resolved_pointers//ptr[substring-after(@from, '#') = current()/@xml:id]"/>
        <!-- insert the children of the "group" element preceding the relevant pointer into the main document
          (before the targeted element): -->
        <xsl:copy-of select="$pointer/preceding-sibling::group[1]/node()"></xsl:copy-of>
        <!-- now copy the targeted element: -->
        <xsl:copy-of select="."></xsl:copy-of>
      </xsl:when>
      <!-- if the element is targeted by @to, i.e. it should become the last element of a virtual division: -->
      <xsl:when test="@xml:id = (for $i in $grouped_structure_resolved_pointers//ptr/@to return substring-after($i, '#'))">
        <xsl:variable name="pointer" select="$grouped_structure_resolved_pointers//ptr[substring-after(@to, '#') = current()/@xml:id]"/>
        <!-- first copy the targeted element: -->
        <xsl:copy-of select="."></xsl:copy-of>
        <!-- now insert the children of the "group" element following the relevant pointer into the main document: -->
        <xsl:copy-of select="$pointer/following-sibling::group[1]/node()"></xsl:copy-of>
      </xsl:when>
      <!-- if the element is targeted by @from AND @to, i.e. it should become the ONLY element of a virtual division: 
      TODO
      -->
      <!--<xsl:when test="
        @xml:id = (for $i in $grouped_structure_resolved_pointers//ptr/@from return substring-after($i, '#'))
        and
        @xml:id = (for $i in $grouped_structure_resolved_pointers//ptr/@to return substring-after($i, '#'))
        ">
        <xsl:variable name="from_pointer" select="$grouped_structure_resolved_pointers//ptr[substring-after(@from, '#') = current()/@xml:id]"/>
        <xsl:variable name="to_pointer" select="$grouped_structure_resolved_pointers//ptr[substring-after(@to, '#') = current()/@xml:id]"/>
        <!-\- insert the children of the "group" element preceding the relevant pointer into the main document
          (before the targeted element): -\->
        <xsl:copy-of select="$from_pointer/preceding-sibling::group[1]/node()"></xsl:copy-of>
        <!-\- now copy the targeted element: -\->
        <xsl:copy-of select="."></xsl:copy-of>
        <!-\- now insert the children of the "group" element following the relevant pointer into the main document: -\->
        <xsl:copy-of select="$to_pointer/following-sibling::group[1]/node()"></xsl:copy-of>        
      </xsl:when>-->
    </xsl:choose>
  </xsl:template>
  
</xsl:stylesheet>
