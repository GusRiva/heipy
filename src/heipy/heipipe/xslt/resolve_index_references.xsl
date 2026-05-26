<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  >

<!-- 
    aim:
        Resolve the ptr elements to index files. This could mean different things 
        based on the position of the reference:
        - Replacing the ptr with the elements pointed at
        - Adding the source attribute
        - Changing the path of the link to match the structure in the database
    author: 
        Gustavo Fernández Riva
-->  
     
  <xsl:output method="xml"/>

  <!-- Absolute URI of the source file, injected by the Python pipeline so that
       relative paths in prefixDef/@replacementPattern resolve correctly even when
       the document was parsed from a string (which has no inherent base URI). -->
  <xsl:param name="sourceBaseUri" as="xs:string?" select="()"
             xmlns:xs="http://www.w3.org/2001/XMLSchema"/>

  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />
  
  <!--<xsl:template match="//text"></xsl:template>
  <xsl:template match="//facsimile"></xsl:template>-->
  
  
  
  <xsl:template match="/TEI/teiHeader/fileDesc/sourceDesc">
    <xsl:choose>
      <xsl:when test="ptr">
        <xsl:copy>
          <xsl:variable name="target" select="ptr/@target"/>
          <xsl:variable name="target_prefix" select="substring-before($target, ':')"/>
          <xsl:variable name="target_local_id" select="substring-after($target, ':')"/>
          <xsl:variable name="prefixDef"
            select="//prefixDef[@ident = $target_prefix]"/>
          <xsl:variable name="file" 
            select="substring-before($prefixDef/@replacementPattern, '$1')"/>
          <xsl:attribute name="source" select="$target"/>
          <xsl:variable name="resolved_file"
            select="if ($sourceBaseUri) then resolve-uri($file, $sourceBaseUri) else $file"/>
          <xsl:copy-of select="document($resolved_file)//*[@xml:id = $target_local_id]"/>
        </xsl:copy>
      </xsl:when>
      <xsl:otherwise>
        <xsl:copy>
          <xsl:apply-templates select="node()"/>  
        </xsl:copy>
      </xsl:otherwise>
    </xsl:choose>
    
    
  </xsl:template>
  
</xsl:stylesheet>
