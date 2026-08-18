<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="3.0" xmlns:hei="https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS" xmlns="http://www.tei-c.org/ns/1.0" xpath-default-namespace="http://www.tei-c.org/ns/1.0">

	<xsl:output method="xml"/>

	<xsl:mode on-no-match="shallow-copy"/>
	<xsl:mode name="reg-levels" on-no-match="shallow-copy"/>
	<xsl:mode name="triplet" on-no-match="shallow-copy"/>

	<xsl:variable name="has-standard-reg" select="exists(//reg/@ana[. = 'hc:StandardMHGRegularization'])"/>

	<xsl:template match="/">
		<xsl:choose>
			<xsl:when test="$has-standard-reg">
				<xsl:apply-templates mode="reg-levels"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:copy-of select="."/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template match="choice[orig][reg]" mode="reg-levels">
		<xsl:copy>
			<xsl:choose>
				<xsl:when test="count(orig | reg) = 3">
					<xsl:apply-templates mode="triplet"/>
				</xsl:when>
				<xsl:otherwise>
					<xsl:apply-templates mode="reg-levels"/>
				</xsl:otherwise>
			</xsl:choose>

		</xsl:copy>
	</xsl:template>

	<xsl:template match="orig" mode="reg-levels">
		<xsl:copy>
			<xsl:if test="following-sibling::reg[@ana => contains('hc:StandardMHGRegularization')]">
				<xsl:attribute name="hei:additiveRegularizationLevel">1</xsl:attribute>
			</xsl:if>
			<xsl:apply-templates mode="reg-levels"/>
		</xsl:copy>

	</xsl:template>

	<xsl:template match="reg" mode="reg-levels">
		<xsl:choose>

			<xsl:when test="@ana => contains('hc:StandardMHGRegularization')">

				<xsl:copy>
					<xsl:attribute name="hei:additiveRegularizationLevel">2</xsl:attribute>
					<xsl:apply-templates select="@* except @hei:additiveRegularizationLevel | node()" mode="reg-levels"/>
				</xsl:copy>

			</xsl:when>

			<xsl:otherwise>

				<xsl:copy>
					<xsl:attribute name="hei:additiveRegularizationLevel">1</xsl:attribute>
					<xsl:apply-templates select="@* except @hei:additiveRegularizationLevel | node()" mode="reg-levels"/>
				</xsl:copy>

				<xsl:copy>
					<xsl:attribute name="hei:additiveRegularizationLevel">2</xsl:attribute>
					<xsl:apply-templates select="@* except @hei:additiveRegularizationLevel | node()" mode="reg-levels"/>
				</xsl:copy>

			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>


	<xsl:template match="orig" mode="triplet">
		<xsl:copy>
			<xsl:apply-templates mode="triplet"/>
		</xsl:copy>
	</xsl:template>

	<xsl:template match="reg" mode="triplet">
		<xsl:copy>
			<xsl:choose>
				<xsl:when test="position() = 2">
					<xsl:attribute name="hei:additiveRegularizationLevel">1</xsl:attribute>
					<xsl:apply-templates select="@* except @hei:additiveRegularizationLevel | node()" mode="triplet"/>
				</xsl:when>
				<xsl:when test="position() = 3">
					<xsl:attribute name="hei:additiveRegularizationLevel">2</xsl:attribute>
					<xsl:apply-templates select="@* except @hei:additiveRegularizationLevel | node()" mode="triplet"/>
				</xsl:when>
			</xsl:choose>

		</xsl:copy>
	</xsl:template>

</xsl:stylesheet>
