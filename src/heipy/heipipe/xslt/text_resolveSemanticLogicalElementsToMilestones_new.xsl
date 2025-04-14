<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0"
  xmlns:xs="http://www.w3.org/2001/XMLSchema"
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:map="http://www.w3.org/2005/xpath-functions/map"

  >

<!-- 
    aim:
          resolving semantic-logical elements which are not allowed as content of <line> to <milestone> and <anchor> pairs, 
          for use in the sourceDoc encoding
          
    logic: 
          - the variable $map provides a map of element names and corresponding heiEDITIONS Concepts resources
          - the semantic-logical container elements whose names are listed in $map are resolved to a <milestone> and 
            an <anchor> (connected by @spanTo) and the original element content between those two empty markers
          - element-specific rules decide how a @ana is constructed on the new <milestone> and 
              which further attributes are copied from the original container element
              
    CAVEAT:
          - for the correct resolving of <rs> the transformation with text_addAnaToRs.xsl needs to be run first
-->  
  
  
  <xsl:variable name="map" select="map{
    'ab' : 'hc:Chunk',
    'address' : 'hc:Address',
    'addrLine' : 'hc:AddressLine',
    'back' : 'hc:ExpressionBack',
    'byline' : 'hc:Byline',
    'body' : 'hc:ExpressionBody',
    'closer' : 'hc:Closer',
    'cue' : 'hc:Cue',
    'date' : 'hc:DateIndication',
    'dateline' : 'hc:Dateline',
    'div' : 'hc:SemanticLogicalDivision',
    'docDate' : 'hc:ExpressionDate',
    'docTitle' : 'hc:ExpressionTitle',
    'epigraph' : 'hc:Epigraph',
    'front' : 'hc:ExpressionFront',
    'fw' : 'OrientationControlIndicator',
    'head' : 'hc:Heading',
    'item' : 'hc:ListItem',
    'l' : 'hc:Verse',
    'label' : 'hc:LabelLikeHeading',
    'lg' : 'hc:VerseGroup',
    'list' : 'hc:List',
    'name' : 'hc:Name',
    'note' : 'hc:Note',
    'orgName' : 'hc:OrganizationName',
    'opener' : 'hc:Opener',
    'p' : 'hc:Paragraph',    
    'persName' : 'hc:PersonName',
    'placeName' : 'hc:PlaceName',
    'postscript' : 'hc:Postscript',
    'rs' : 'hc:ReferencingString',
    'salute' : 'hc:Salutation',
    'signed' : 'hc:Signature',
    'sp': 'hc:Speech',
    'spGrp': 'hc:SpeechGroup',
    'stage': 'hc:StageDirection',
    'term' : 'hc:SubjectReference',
    'text' : 'hc:TextualExpression',
    'title' : 'hc:WorkTitle', 
    'titlePage' : 'hc:TitlePage',
    'titlePart' : 'hc:ExpressionTitlePart',
    'trailer' : 'hc:Trailer'
    }"/>
     
  <xsl:output method="xml"/>

  <xsl:param name="randomDocId" as="xs:boolean" select="false()"/>

  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />


  <!-- transform all elements whose names are included in $map above as keys and which are not members of hc:EditorialContent -->
  <xsl:template match="*[map:contains($map, local-name())][ancestor-or-self::text][not(ancestor-or-self::*[tokenize(@ana, '\s+') = ('hc:EditorialContent', 'hc:FigureDescription')])]">
    <xsl:choose>
      <!-- conditions stopping the resolving algorithm in the first place: -->
      <xsl:when test="self::*[parent::figure or parent::table]">
        <!-- copy the element unchanged: -->
        <xsl:copy>
          <xsl:copy-of select="@*"></xsl:copy-of>
          <xsl:copy-of select="node()"></xsl:copy-of>
        </xsl:copy>
      </xsl:when>
      <!-- otherwise the container element shall be resolved into milestone-anchor pairs: -->
      <xsl:otherwise>
        <xsl:variable name="rndNumber">
          <xsl:choose>
            <xsl:when test="$randomDocId">
              <xsl:value-of select="format-number(random-number-generator()?number, '.#####')"/>
            </xsl:when>
            <xsl:otherwise>
              <xsl:value-of select="''"/>
            </xsl:otherwise>
          </xsl:choose>
        </xsl:variable>
        <xsl:variable name="id" select="generate-id() || $rndNumber"/>
        <xsl:choose>
          <xsl:when test="local-name() = ('persName', 'placeName', 'orgName', 'term', 'title')">
            <xsl:element name="milestone" namespace="http://www.tei-c.org/ns/1.0">
              <xsl:copy-of select="@xml:id"></xsl:copy-of>         
              <xsl:attribute name="ana" select="$map(local-name())"></xsl:attribute>
              <xsl:attribute name="corresp" select="'#' || $id"></xsl:attribute>
              <xsl:copy-of select="@ref"></xsl:copy-of>
            </xsl:element>
          </xsl:when>
          <xsl:when test="local-name() = ('rs', 'name')">
            <xsl:element name="milestone" namespace="http://www.tei-c.org/ns/1.0">
              <xsl:copy-of select="@xml:id"></xsl:copy-of>          
              <xsl:choose>
                <xsl:when test="@ana">
                  <xsl:copy-of select="@ana"></xsl:copy-of>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:attribute name="ana" select="$map(local-name())"></xsl:attribute>
                </xsl:otherwise>
              </xsl:choose>
              <xsl:copy-of select="@ref"></xsl:copy-of>
              <xsl:attribute name="corresp" select="'#' || $id"></xsl:attribute>
            </xsl:element>      
          </xsl:when>
          <xsl:when test="local-name() = ('date', 'docDate')">
            <xsl:element name="milestone" namespace="http://www.tei-c.org/ns/1.0">
              <xsl:copy-of select="@xml:id"></xsl:copy-of>
              <xsl:attribute name="ana" select="$map(local-name())"></xsl:attribute>
              <xsl:attribute name="corresp" select="'#' || $id"></xsl:attribute>
              <xsl:copy-of select="@when"></xsl:copy-of>
              <xsl:copy-of select="@from"></xsl:copy-of>
              <xsl:copy-of select="@to"></xsl:copy-of>
              <xsl:copy-of select="@notBefore"></xsl:copy-of>
              <xsl:copy-of select="@notAfter"></xsl:copy-of>
            </xsl:element>       
          </xsl:when>
          <xsl:when test="local-name() = 'div'">
            <xsl:element name="milestone" namespace="http://www.tei-c.org/ns/1.0">
              <xsl:choose>
                <xsl:when test="@ana">
                  <xsl:copy-of select="@ana"></xsl:copy-of>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:attribute name="ana" select="$map(local-name())"></xsl:attribute>
                </xsl:otherwise>
              </xsl:choose>
              <xsl:copy-of select="@xml:id"></xsl:copy-of>          
              <xsl:copy-of select="@n"></xsl:copy-of>          
              <xsl:attribute name="corresp" select="'#' || $id"></xsl:attribute>
            </xsl:element>      
          </xsl:when>
          <xsl:when test="local-name() = ('ab', 'address', 'note')">
            <xsl:element name="milestone" namespace="http://www.tei-c.org/ns/1.0">
              <xsl:copy-of select="@xml:id"></xsl:copy-of>
              <xsl:choose>
                <xsl:when test="@ana">
                  <xsl:copy-of select="@ana"></xsl:copy-of>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:attribute name="ana" select="$map(local-name())"></xsl:attribute>
                </xsl:otherwise>
              </xsl:choose>
              <xsl:attribute name="corresp" select="'#' || $id"></xsl:attribute>
            </xsl:element>     
          </xsl:when>
          <xsl:when test="local-name() = ('label', 'fw')">
            <xsl:element name="milestone" namespace="http://www.tei-c.org/ns/1.0">
              <xsl:copy-of select="@xml:id"></xsl:copy-of>
              <xsl:choose>
                <xsl:when test="@ana">
                  <xsl:copy-of select="@ana"></xsl:copy-of>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:attribute name="ana" select="$map(local-name())"></xsl:attribute>
                </xsl:otherwise>
              </xsl:choose>
              <xsl:attribute name="corresp" select="'#' || $id"></xsl:attribute>
            </xsl:element>     
          </xsl:when>
          <xsl:when test="local-name() = 'l'">
            <xsl:element name="milestone" namespace="http://www.tei-c.org/ns/1.0">
              <xsl:copy-of select="@xml:id"></xsl:copy-of>
              <xsl:choose>
                <xsl:when test="@ana">
                  <xsl:attribute name="ana" select="$map(local-name()) || ' ' || @ana"></xsl:attribute>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:attribute name="ana" select="$map(local-name())"></xsl:attribute>
                </xsl:otherwise>
              </xsl:choose>
              <xsl:copy-of select="@n"></xsl:copy-of>
              <xsl:copy-of select="@hei:altN"></xsl:copy-of>
              <xsl:attribute name="corresp" select="'#' || $id"></xsl:attribute>
            </xsl:element>     
          </xsl:when>     
          <xsl:when test="local-name() = 'text'">
            <xsl:element name="milestone" namespace="http://www.tei-c.org/ns/1.0">
              <xsl:copy-of select="@xml:id"></xsl:copy-of>
              <xsl:choose>
                <xsl:when test="@ana">
                  <xsl:attribute name="ana" select="$map(local-name()) || ' ' || @ana"></xsl:attribute>
                </xsl:when>
                <xsl:otherwise>
                  <xsl:attribute name="ana" select="$map(local-name())"></xsl:attribute>
                </xsl:otherwise>
              </xsl:choose>
              <xsl:attribute name="corresp" select="'#' || $id"></xsl:attribute>
            </xsl:element>     
          </xsl:when>     
          <xsl:when test="local-name() = 'head'">
            <xsl:element name="milestone" namespace="http://www.tei-c.org/ns/1.0">
              <xsl:copy-of select="@xml:id"></xsl:copy-of>  
              <xsl:attribute name="ana" select="$map(local-name())"></xsl:attribute>
              <xsl:copy-of select="@n"></xsl:copy-of>
              <xsl:attribute name="corresp" select="'#' || $id"></xsl:attribute>
            </xsl:element>     
          </xsl:when>     
          <xsl:otherwise>
            <xsl:element name="milestone" namespace="http://www.tei-c.org/ns/1.0">
              <xsl:copy-of select="@xml:id"></xsl:copy-of>
              <xsl:attribute name="ana" select="$map(local-name())"></xsl:attribute>
              <xsl:attribute name="corresp" select="'#' || $id"></xsl:attribute>
            </xsl:element>
          </xsl:otherwise>
        </xsl:choose>    
        <xsl:apply-templates></xsl:apply-templates>
        <xsl:element name="anchor" namespace="http://www.tei-c.org/ns/1.0">
          <xsl:attribute name="xml:id" select="$id"></xsl:attribute>
        </xsl:element>
      </xsl:otherwise>
    </xsl:choose>    
  </xsl:template>
  
</xsl:stylesheet>
