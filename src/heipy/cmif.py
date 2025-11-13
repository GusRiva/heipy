import argparse
import datetime
import hashlib
import sys
import importlib.resources

import os
import re
from lxml import etree as et
import uuid
from .namespaces import ns, prefix_format

issues_in_CMIF_export = {}


def prettyprint(element: et.Element, **kwargs) -> None:
    xml = et.tostring(element, pretty_print=True, **kwargs)
    print(xml.decode(), end='')
    return


def set_cmif_correspAction_type(correspAction: et.Element, cmif_correspAction: et.Element) -> et.Element:
    """ Transforms the various correspondence types usable in a heiEditions-correspAction-Element to valid cmif Attributes and adds them to the cmif_correspAction-Element."""
    type = correspAction.get("ana")
    if "CorrespondenceAuthoring" in type:
        cmif_correspAction.set("type", "sent")
    elif "DesignationAsCorrespondenceAddressee" in type:
        cmif_correspAction.set("type", "received")
    elif "CorrespondenceReceiving" in type:
        cmif_correspAction.set("type", "received")
    elif "CorrespondenceSending" in type:
        cmif_correspAction.set("type", "sent")
    else:
        print(f"Attribute {correspAction.get('ana')} has not been mapped to a CMIF type (allowed: 'sent' or 'received'), yet. Please correct this in the output and update the mapping.")
    return cmif_correspAction


def add_cmif_persName_to_correspAction(correspAction: et.Element, cmif_correspAction: et.Element) -> et.Element:
    cmif_persName = et.SubElement(cmif_correspAction, "persName")
    cmif_persName.text = correspAction.find(".//tei:persName", namespaces=ns).text

    try:
        cmif_persName.set("ref", correspAction.find(".//tei:idno", namespaces=ns).text)
    except AttributeError:
        pass
    return cmif_correspAction


def add_cmif_placeName_to_correspAction(correspAction: et.Element, cmif_correspAction: et.Element, filename: str) -> et.Element:
    for place_info in correspAction.findall("./tei:location", namespaces=ns):
        cmif_placeName = et.SubElement(cmif_correspAction, "placeName")
        cmif_placeName.text = place_info.find("./tei:placeName", namespaces=ns).text
        geonames_idno = place_info.find("./tei:idno[@ana = 'hc:GeonamesURI']", namespaces=ns).text
        if geonames_idno is not None:
            cmif_placeName.set("ref", geonames_idno)
        else:
            message = f"Included {cmif_placeName.text} without Geonames-ID."
            try:
                issues_in_CMIF_export[cmif_placeName.text].append((filename, message))
            except KeyError:
                issues_in_CMIF_export.update({cmif_placeName.text: [(filename, message)]})
        cmif_correspAction.append(cmif_placeName)
    return cmif_correspAction


def add_cmif_date_to_correspAction(correspAction: et.Element, cmif_correspAction: et.Element) -> et.Element:
    for date in correspAction.findall("./tei:date", namespaces=ns):
        cmif_date = et.SubElement(cmif_correspAction, "date")
        for attr, val in date.attrib.items():
            cmif_date.set(attr, val)
        cmif_correspAction.append(cmif_date)
    return cmif_correspAction


def create_cmif_correspAction(correspAction: et.Element, filename: str) -> et.Element:
    cmif_correspAction = et.Element("correspAction")
    cmif_correspAction = set_cmif_correspAction_type(correspAction, cmif_correspAction)
    cmif_correspAction = add_cmif_persName_to_correspAction(correspAction, cmif_correspAction)
    cmif_correspAction = add_cmif_placeName_to_correspAction(correspAction, cmif_correspAction, filename)
    cmif_correspAction = add_cmif_date_to_correspAction(correspAction, cmif_correspAction)
    return cmif_correspAction


def create_cmif_correspDesc(doc: et.Element, ref: str, edition_uuid: str, filename: str) -> et.Element:
    cmif_correspDesc = et.Element("correspDesc", nsmap=ns, ref=ref, source='#' + edition_uuid, key=filename[:-4])
    try:
        correspDesc = doc.xpath("//tei:correspDesc", namespaces=ns)[0]
    except IndexError:
        correspDesc = doc.xpath("//tei:correspDesc", namespaces=ns)
    for correspAction in correspDesc:
        cmif_correspAction = create_cmif_correspAction(correspAction, filename)
        cmif_correspDesc.append(cmif_correspAction)
    return cmif_correspDesc


def write_xml_to_file(xml: et.ElementTree, output_path: str) -> None:
    et.indent(xml)
    if not output_path.endswith("/"):
        output_path += "/"
    try:
        xml.write(output_path + "CMIF_Export.xml", xml_declaration=True, pretty_print=True, encoding="UTF-8")
    except FileNotFoundError:
        os.makedirs(output_path, exist_ok=True)
        print(f"The given directory in output_path was created as it couldn't be found previously: {output_path}")
        xml.write(output_path + "CMIF_Export.xml", xml_declaration=True, pretty_print=True, encoding="UTF-8")
    return


def create_xml_suitable_uuid_from_string(value: str) -> str:
    """Creates a hex representation of the input string (e.g. a DOI) and transforms it into a UUID. If the first character of the UUID is
    a number, it is replaced with a character in order to allow the UUID to be used as a valid xml:id"""
    hex_string = hashlib.md5(value.encode("UTF-8")).hexdigest()
    id = str(uuid.UUID(hex=hex_string))
    if id[0].isnumeric(): # would lead to an invalid XML id
        x = "0123456789"
        y = "abcdefghij"
        translation_table = str.maketrans(x, y)
        id = id[0].translate(translation_table) + id[1:]
    return str(id)


def get_edition_metadata_from_file(doc: et.Element) -> tuple[str | None, str| None, str|None]:
    """Extracts metadata about the Edition from the TEI-Header of a file. 
    For the DOI, the EditionWebsiteIdentifier is used;
    for title and citation the bibl-Element @ana=hc:RecommendedBibliographicReferenceForEditionWebsite.
    """
    try:
        edition_doi = [idno for idno in doc.findall(".//tei:idno", namespaces=ns) if "hc:EditionWebsiteIdentifier" in idno.attrib["ana"]][0].text
    except:
        edition_doi = None

    try:
        edition_bibl_element = [bibl for bibl in doc.findall(".//tei:bibl", namespaces=ns) if "hc:RecommendedBibliographicReferenceForEditionWebsite" in bibl.attrib["ana"]][0] # Todo: DOI-Element aufnehmen
        edition_bibl = ''.join(edition_bibl_element.itertext())

        edition_title = re.split(",", edition_bibl, 1)[0] if edition_bibl is not None else None
    except:
        edition_bibl, edition_title = None, None
    return edition_doi, edition_bibl, edition_title


def initialize_cmif_file(project_name: str) -> tuple[et.ElementTree, et.Element, et.Element, et.Element]: # Datei in templates auslagern
    with importlib.resources.path("heipy.templates", "cmif_template.xml") as template_path:
        template_file = open(template_path, "rb")
        cmif = et.parse(template_file)
        profileDesc = cmif.find(".//tei:profileDesc", namespaces=ns)
        bibl = cmif.find(".//tei:bibl", namespaces=ns)
        title = cmif.find(".//tei:title", namespaces=ns)
        date = cmif.find(".//tei:date", namespaces=ns)
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        date.set("when", current_date)
        idno_url = cmif.find(".//tei:publicationStmt/tei:idno", namespaces=ns)
        idno_url.text = "https://digi.ub.uni-heidelberg.de/editionService/cmif/" + project_name
    return cmif, profileDesc, bibl, title


def add_edition_metadata_to_cmif(doc: et.Element, bibl: et.Element, title: et.Element) -> tuple[True | False, str | None]:
    edition_doi, edition_bibl, edition_title = get_edition_metadata_from_file(doc)
    edition_uuid = create_xml_suitable_uuid_from_string(edition_doi)
    if not edition_uuid or not edition_title or not edition_bibl:
        return False, None
    else:
        bibl.text = edition_bibl
        bibl.set(prefix_format('xml', 'id'), edition_uuid)
        title.text = title.text + "“" + edition_title + "”"
    return True, edition_uuid


def doc_is_correspondence(doc: et.Element) -> tuple[True | False]:
    doc_type = doc.find(".//tei:text", namespaces=ns).attrib["ana"]
    correspondence_types = ["hc:Letter", "hc:LetterCard", "hc:PicturePostcard", "hc:Postcard", "hc:Telegram"]     # envelope nicht (nur an div)
    for type in correspondence_types:
        if type in doc_type:
            return True
    return False


def create_cmif_export(files: list, project_name: str, output_path: str):
    cmif, cmif_profileDesc, cmif_bibl, cmif_title = initialize_cmif_file(project_name)
    added_edition_metadata_to_cmif = False

    for file in files:
        doc = et.parse(file).getroot()

        if not doc_is_correspondence(doc):
            issues_in_CMIF_export.update({
                                             file: f"Document's type is not included in correspondence types; thus the file is not included in CMIF export."})
            continue
        if not added_edition_metadata_to_cmif:
            added_edition_metadata_to_cmif, edition_uuid = add_edition_metadata_to_cmif(doc, cmif_bibl, cmif_title)
        try:
            edition_doi = [idno for idno in doc.findall(".//tei:idno", namespaces=ns) if
                           "hc:ReadingViewIdentifier" in idno.attrib["ana"]][
                0].text  # TODO: ref von SourceView, wenn kein ReadingViewref vorhanden?
        except IndexError:
            issues_in_CMIF_export.update(
                {file: "No ReadingViewIdentifier found. File is not included in CMIF export."})
            continue

        cmif_correspDesc = create_cmif_correspDesc(doc, edition_doi, edition_uuid, file)
        cmif_profileDesc.append(cmif_correspDesc)

    write_xml_to_file(cmif, output_path)
    print(issues_in_CMIF_export)
    return

