<?xml version="1.0" encoding="utf-8"?>
<xsl:stylesheet 
  version="3.0"
  xpath-default-namespace="http://www.tei-c.org/ns/1.0" 
  xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  >

<!-- 
    
-->  
     
  <xsl:output method="xml"/>

  <!-- Identity template -->
  <xsl:mode on-no-match="shallow-copy" />
  
  <xsl:param name="rendition" select="'remove'"></xsl:param>
  <!-- "remove" is the default behavior of this script; other supported values are:
          "keep": all @rendition attributes will be kept
          "configuration": a specific configuration about the heiEDITIONS classes to be included or excluded from @rendition
                    needs to be processed: in this case the additional parameter $configuration must specify the path to the
                    configuration file to be evaluated
  -->
  
  <xsl:param name="color" select="'remove'"></xsl:param>
  <!-- 
    "remove" is the default behavior - it means that the attribute hei:color is removed everywhere;
    
    the other supported value ist:
    
    "keep": in this case @hei:color will be kept everywhere
  -->
  
  <xsl:param name="configuration"></xsl:param>
  
  <xsl:variable name="inclusions">
    <xsl:if test="doc($configuration)/hei:configuration/hei:renditionFilter/hei:include">
      <xsl:if test="doc($configuration)/hei:configuration/hei:renditionFilter/hei:include/hei:class[not(@onElement)]">
        <hei:universal>
          <xsl:for-each select="doc($configuration)/hei:configuration/hei:renditionFilter/hei:include/hei:class[not(@onElement)]">
            <hei:class>
              <xsl:value-of select="normalize-space(.)"/>
            </hei:class>
          </xsl:for-each>
        </hei:universal>
      </xsl:if>
      <xsl:if test="doc($configuration)/hei:configuration/hei:renditionFilter/hei:include/hei:class[@onElement]">
        <hei:specific>
          <xsl:for-each select="doc($configuration)/hei:configuration/hei:renditionFilter/hei:include/hei:class[@onElement]">
            <xsl:variable name="current_class" select="normalize-space(.)"/>
            <xsl:for-each select="tokenize(@onElement, '\s+')">
              <hei:item>
                <hei:class>
                  <xsl:value-of select="$current_class"/>
                </hei:class>
                <hei:element>
                  <xsl:value-of select="substring-after(., '}')"/>
                </hei:element>
                <hei:namespace>
                  <xsl:value-of select="substring-after(., '{') => substring-before('}')"/>
                </hei:namespace>
              </hei:item>
            </xsl:for-each>
          </xsl:for-each>
        </hei:specific>
      </xsl:if>
    </xsl:if>
  </xsl:variable>
  
  <xsl:variable name="exclusions">
    <xsl:if test="doc($configuration)/hei:configuration/hei:renditionFilter/hei:exclude">
      <xsl:if test="doc($configuration)/hei:configuration/hei:renditionFilter/hei:exclude/hei:class[not(@onElement)]">
        <hei:universal>
          <xsl:for-each select="doc($configuration)/hei:configuration/hei:renditionFilter/hei:exclude/hei:class[not(@onElement)]">
            <hei:class>
              <xsl:value-of select="normalize-space(.)"/>
            </hei:class>
          </xsl:for-each>
        </hei:universal>
      </xsl:if>
      <xsl:if test="doc($configuration)/hei:configuration/hei:renditionFilter/hei:exclude/hei:class[@onElement]">
        <hei:specific>
          <xsl:for-each select="doc($configuration)/hei:configuration/hei:renditionFilter/hei:exclude/hei:class[@onElement]">
            <xsl:variable name="current_class" select="normalize-space(.)"/>
            <xsl:for-each select="tokenize(@onElement, '\s+')">
              <hei:item>
                <hei:class>
                  <xsl:value-of select="$current_class"/>
                </hei:class>
                <hei:element>
                  <xsl:value-of select="substring-after(., '}')"/>
                </hei:element>
                <hei:namespace>
                  <xsl:value-of select="substring-after(., '{') => substring-before('}')"/>
                </hei:namespace>
              </hei:item>
            </xsl:for-each>
          </xsl:for-each>
        </hei:specific>
      </xsl:if>
    </xsl:if>
  </xsl:variable>
    
  <xsl:template match="*[@rendition or @hei:color]|hei:initial">
    
    <xsl:variable name="current_element_name" select="local-name()"/>
    
    <xsl:choose>
      
      <!-- with the parameter $rendition set to "keep" all visual information remains preserved -->
      <xsl:when test="$rendition = 'keep'">
        <xsl:copy>
          <xsl:copy-of select="@*|node()"></xsl:copy-of>
        </xsl:copy>
      </xsl:when>
      
      <!-- with the parameter $rendition set to "configuration" and the parameter $configuration set (must be a path to a configuration file) -->
      <xsl:when test="$rendition = 'configuration' and $configuration">
        <xsl:choose>
          <xsl:when test="$inclusions != ''">
            <!-- if 
                        the current element carries one of the to-be-included classes in @rendition 
                        AND 
                            (
                            the current element name is specified on hei:class/@onElement
                            OR
                            there is no @onElement on the hei:class in question
                            )
                   then:
                      keep the element as is but copy only rendition classes to be included
            -->
            <xsl:variable name="current_renditions" select="(for $i in tokenize(@rendition, '\s+') return substring-after($i, 'hc:'))"/>
           
            <xsl:variable name="keep_renditions" as="item()*">
              <xsl:for-each select="$inclusions/hei:specific/hei:item[hei:element = $current_element_name]">
                <xsl:value-of select="hei:class"/>
              </xsl:for-each>
              <xsl:for-each select="$inclusions/hei:universal/hei:class">
                <xsl:value-of select="."/>
              </xsl:for-each>
            </xsl:variable>
            
            <xsl:variable name="new_renditions_sequence" as="item()*">
              <xsl:for-each select="$current_renditions">
                <xsl:if test=". = $keep_renditions">
                  <xsl:copy-of select="."></xsl:copy-of>
                </xsl:if>
              </xsl:for-each>
            </xsl:variable>
            
            <xsl:choose>
                            <!-- if the element is seg or hi and there are no attributes other than rendition or hei:color
          the element will be removed and only its node content will be copied or processed further:
          -->
              <xsl:when test="
                $current_element_name = ('seg', 'hi') 
                and 
                not(@*[not(local-name() = ('rendition', 'color'))])
                and
                count($new_renditions_sequence) = 0
                ">
                <xsl:apply-templates></xsl:apply-templates>
              </xsl:when>
              <xsl:otherwise>
                <xsl:copy>
                  <xsl:copy-of select="@*[not(local-name() = ('rendition', 'color'))]"></xsl:copy-of>
                  <xsl:if test="count($new_renditions_sequence) > 0">
                    <xsl:attribute name="rendition" select="string-join(for $i in $new_renditions_sequence return 'hc:' || $i, ' ')"></xsl:attribute>
                  </xsl:if>                 
                  <xsl:if test="$color = 'keep'">
                    <xsl:copy-of select="@hei:color"></xsl:copy-of>
                  </xsl:if>
                  <xsl:apply-templates></xsl:apply-templates>
                </xsl:copy>
              </xsl:otherwise>
            </xsl:choose>        
            
          </xsl:when>
          
          <xsl:when test="$exclusions != ''">
            
            <!-- if 
                        the current element carries one of the to-be-excluded classes in @rendition 
                        AND 
                            (
                            the current element name is specified on hei:class/@onElement
                            OR
                            there is no @onElement on the hei:class in question
                            )
                   then:
                      keep the element as is but copy only rendition classes to be included
            -->
            <xsl:variable name="current_renditions" select="(for $i in tokenize(@rendition, '\s+') return substring-after($i, 'hc:'))"/>
            
            <xsl:variable name="exclude_renditions" as="item()*">
              <xsl:for-each select="$exclusions/hei:specific/hei:item[hei:element = $current_element_name]">
                <xsl:value-of select="hei:class"/>
              </xsl:for-each>
              <xsl:for-each select="$exclusions/hei:universal/hei:class">
                <xsl:value-of select="."/>
              </xsl:for-each>
            </xsl:variable>
            
            <xsl:variable name="new_renditions_sequence" as="item()*">
              <xsl:for-each select="$current_renditions">
                <xsl:if test="not(. = $exclude_renditions)">
                  <xsl:copy-of select="."></xsl:copy-of>
                </xsl:if>
              </xsl:for-each>
            </xsl:variable>
            
            <xsl:choose>
              <!-- if the element is seg or hi and there are no attributes other than rendition or hei:color
          the element will be removed and only its node content will be copied or processed further:
          -->
              <xsl:when test="
                $current_element_name = ('seg', 'hi') 
                and 
                not(@*[not(local-name() = ('rendition', 'color'))])
                and
                count($new_renditions_sequence) = 0
                ">
                <xsl:apply-templates></xsl:apply-templates>
              </xsl:when>
              <!-- only classes which haven't been excluded are kept on @rendition -->
              <xsl:otherwise>
                <xsl:copy>
                  <xsl:copy-of select="@*[not(local-name() = ('rendition', 'color'))]"></xsl:copy-of>
                  <xsl:if test="count($new_renditions_sequence) > 0">
                    <xsl:attribute name="rendition" select="string-join(for $i in $new_renditions_sequence return 'hc:' || $i, ' ')"></xsl:attribute>
                  </xsl:if>
                  <xsl:if test="$color = 'keep'">
                    <xsl:copy-of select="@hei:color"></xsl:copy-of>
                  </xsl:if>
                  <xsl:apply-templates></xsl:apply-templates>
                </xsl:copy>
              </xsl:otherwise>
            </xsl:choose>        
            
          </xsl:when>
        </xsl:choose>
      </xsl:when>
      
      <!-- with the default behavior or with the parameter $rendition explicitly set to "remove"-->
      <xsl:otherwise>
        <xsl:choose>
          <!-- if the element is seg or hi and there are no attributes other than rendition or hei:color
            and the parameter $color is not set to "keep"
          the element will be removed and only its node content will be copied or processed further:
          -->
          <xsl:when test="
            local-name() = ('seg', 'hi') 
            and 
            not(@*[not(local-name() = ('rendition', 'color'))])
            and
            not($color = 'keep')">
            <xsl:apply-templates></xsl:apply-templates>
          </xsl:when>
          <!-- if there is @hei:color and the parameter $color ist set to "keep"
          then the element is kept with all attributes except @rendition:
          -->
          <xsl:when test="@hei:color and $color = 'keep'">
            <xsl:copy>
              <xsl:copy-of select="@*[not(local-name() = 'rendition')]"></xsl:copy-of>
              <xsl:apply-templates></xsl:apply-templates>
            </xsl:copy>
          </xsl:when>
          <!-- in all other cases the attributes @rendition and @hei:color are removed and the element kept: -->
          <xsl:otherwise>
            <xsl:copy>
              <xsl:copy-of select="@*[not(local-name() = ('rendition', 'color'))]"></xsl:copy-of>
              <xsl:apply-templates></xsl:apply-templates>
            </xsl:copy>
          </xsl:otherwise>
        </xsl:choose>        
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
</xsl:stylesheet>
