<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs"    
     version="3.0" xpath-default-namespace="http://www.tei-c.org/ns/1.0"
     xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS"
     xmlns:tei="http://www.tei-c.org/ns/1.0"
    >
    
    <!--     Unwraps elements by name and optional attribute name and/or value-->
    
    <xsl:output method="xml"></xsl:output>
    
    <xsl:param name="delenda_name"></xsl:param>
    <xsl:param name="delenda_attr_name"></xsl:param>
    <xsl:param name="delenda_attr_val"></xsl:param>
       
    <!-- Identity template -->
    <xsl:mode on-no-match="shallow-copy" />
    
    
    
    <xsl:template match="element()">
        <xsl:choose>
            
            <xsl:when test="name()= $delenda_name">
                <xsl:choose>
                    <xsl:when test="string-length($delenda_attr_name) lt 1">
                        <!-- Match element name only     -->
                        <xsl:apply-templates select="node()"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:choose>
                            <xsl:when test="@*[name()=$delenda_attr_name]">
                                <xsl:choose>
                                    <xsl:when test="string-length($delenda_attr_val) lt 1">
                                        <!-- Match element and atttribute name     -->
                                        <xsl:apply-templates select="node()"/>        
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:choose>
                                            <xsl:when test="@*[name() = $delenda_attr_name]= $delenda_attr_val">
                                                <!-- Match element and atttribute name and also attribute value  -->
                                                <xsl:apply-templates select="node()"/>        
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:copy>
                                                    <xsl:apply-templates select="node()|@*"/>
                                                </xsl:copy> 
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </xsl:otherwise>
                                </xsl:choose>
                                
                            </xsl:when>
                            <xsl:otherwise>
                                <!-- Normal     -->
                                <xsl:copy>
                                    <xsl:apply-templates select="node()|@*"/>
                                </xsl:copy> 
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:when>
            
            <xsl:otherwise>
            <!-- Normal     -->
                <xsl:copy>
                    <xsl:apply-templates select="node()|@*"/>
                </xsl:copy>
            </xsl:otherwise>
        </xsl:choose>
        
    </xsl:template>
    
    
    
</xsl:stylesheet>