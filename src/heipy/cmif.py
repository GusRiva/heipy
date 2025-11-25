import datetime
import hashlib
import importlib.resources
import uuid
from pathlib import Path
from lxml import etree as et

from .namespaces import ns, prefix_format
from .parsers import heiparse

issues_in_CMIF_export = {}


def set_cmif_correspAction_type(correspAction: et.Element,
                                cmif_correspAction: et.Element,
                                filename:str) -> None:
    """
    Transforms the various correspondence types usable in a heiEditions-correspAction-Element
    to valid cmif Attributes and adds them to the cmif_correspAction-Element.
    """
    ana_type = correspAction.get("ana")
    if ana_type is None:
        print(f"Could not find attribute @ana in correspAction in the file {filename}. Please add the attribute value "
              f"and re-start the CMIF export.")
        return

    if "CorrespondenceAuthoring" in ana_type:
        cmif_correspAction.set("type", "sent")
    elif "DesignationAsCorrespondenceAddressee" in ana_type:
        cmif_correspAction.set("type", "received")
    elif "CorrespondenceReceiving" in ana_type:
        cmif_correspAction.set("type", "received")
    elif "CorrespondenceSending" in ana_type:
        cmif_correspAction.set("type", "sent")
    else:
        print(f"Attribute {ana_type} in file {filename} has not been mapped to a CMIF type "
              "(allowed: 'sent' or 'received'), yet. Please correct this in the output and update the mapping.")

    return


def add_cmif_persName_to_correspAction(correspAction: et.Element, cmif_correspAction: et.Element) -> None:
    cmif_persName = et.SubElement(cmif_correspAction, "persName")
    cmif_persName.text = correspAction.find(".//tei:persName", namespaces=ns).text
    persName_parent = correspAction.find(".//tei:persName", namespaces=ns).getparent()
    persName_idno = persName_parent.find(".//tei:idno[@ana='hc:GNDURI']", namespaces=ns)
    if persName_idno is not None:
        cmif_persName.set("ref", persName_idno.text)
    return


def add_cmif_placeName_to_correspAction(correspAction: et.Element,
                                        cmif_correspAction: et.Element,
                                        filename: str) -> None:
    for place_info in correspAction.findall("./tei:location", namespaces=ns):
        cmif_placeName = et.SubElement(cmif_correspAction, "placeName")
        cmif_placeName.text = place_info.find("./tei:placeName", namespaces=ns).text
        geonames_idno = place_info.find("./tei:idno[@ana = 'hc:GeonamesURI']", namespaces=ns).text
        if geonames_idno is not None:
            cmif_placeName.set("ref", geonames_idno)
        else:
            message = f"Included {cmif_placeName.text} without Geonames-ID."
            issues_in_CMIF_export.setdefault(filename, []).append(message)
        cmif_correspAction.append(cmif_placeName)
    return


def add_cmif_date_to_correspAction(correspAction: et.Element, cmif_correspAction: et.Element) -> None:
    for date in correspAction.findall("./tei:date", namespaces=ns):
        cmif_date = et.SubElement(cmif_correspAction, "date")
        for attr, val in date.attrib.items():
            cmif_date.set(attr, val)
        cmif_correspAction.append(cmif_date)
    return


def create_cmif_correspAction(correspAction: et.Element, filename: str) -> et.Element:
    cmif_correspAction = et.Element("correspAction")
    set_cmif_correspAction_type(correspAction, cmif_correspAction, filename)
    add_cmif_persName_to_correspAction(correspAction, cmif_correspAction)
    add_cmif_placeName_to_correspAction(correspAction, cmif_correspAction, filename)
    add_cmif_date_to_correspAction(correspAction, cmif_correspAction)
    return cmif_correspAction


def create_cmif_correspDesc(doc: et.Element, ref: str, edition_uuid: str, filename: str) -> et.Element:
    cmif_correspDesc = et.Element("correspDesc", ref=ref, source='#' + edition_uuid, key=filename[:-4])
    correspDescs = doc.findall(".//tei:correspDesc", namespaces=ns)
    if not correspDescs:
        issues_in_CMIF_export.setdefault(filename, []).append("No correspDesc-element found. Skipped for CMIF export.")
        return None
    for correspDesc in correspDescs: # if CMIF guidelines are changed and multiple correspDescs should result in multiple cmif_correspDescs, change here
        for correspAction in correspDesc.findall(".//tei:correspAction", namespaces=ns):
            cmif_correspAction = create_cmif_correspAction(correspAction, filename)
            cmif_correspDesc.append(cmif_correspAction)
    return cmif_correspDesc


def write_xml_to_file(xml: et.ElementTree, output_path: str | Path) -> None:
    et.indent(xml)
    output_dir = Path(output_path)

    if output_dir.suffix:
        output_dir = output_dir.parent
    if not output_dir.is_dir():
        print(f"The given directory in output_path was created as it couldn't be found previously: {output_path}")
        output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "CMIF_Export.xml"
    try:
        xml.write(str(output_file), xml_declaration=True, pretty_print=True, encoding="UTF-8")
    except (OSError, PermissionError) as e:
        raise IOError(f"Failed to write CMIF export to {output_file}: {e}") from e
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


def initialize_cmif_file(project_name: str,
                         edition_uuid: str,
                         edition_title: str,
                         edition_citation: str) -> et.ElementTree:
    with importlib.resources.path("heipy.templates", "cmif_template.xml") as template_path:
        template_file = open(template_path, "rb")
        cmif = et.parse(template_file)
        template_file.close()

    bibl = cmif.find(".//tei:bibl", namespaces=ns)
    bibl.set(prefix_format('xml', 'id'), edition_uuid)
    bibl.text = edition_citation

    title = cmif.find(".//tei:title", namespaces=ns)
    title.text = title.text + "“" + edition_title + "”"

    date = cmif.find(".//tei:date", namespaces=ns)
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    date.set("when", current_date)

    idno_url = cmif.find(".//tei:publicationStmt/tei:idno", namespaces=ns)
    idno_url.text = "https://digi.ub.uni-heidelberg.de/editionService/cmif/" + project_name

    return cmif


def doc_is_correspondence(doc: et.Element) -> bool:
    doc_type = doc.find(".//tei:text", namespaces=ns).attrib["ana"]
    correspondence_types = ["hc:Letter",
                            "hc:LetterCard",
                            "hc:PicturePostcard",
                            "hc:Postcard",
                            "hc:Telegram"]     # envelope nicht (nur an div)
    for type in correspondence_types:
        if type in doc_type:
            return True
    return False


def create_cmif_export(files: list,
                       project_name: str,
                       output_path: str | Path,
                       edition_doi: str,
                       edition_title: str,
                       edition_citation: str) -> None:
    edition_uuid = create_xml_suitable_uuid_from_string(edition_doi)
    cmif_tree = initialize_cmif_file(project_name, edition_uuid, edition_title, edition_citation)
    cmif_profileDesc = cmif_tree.find(".//tei:profileDesc", namespaces=ns)

    for file in files:
        doc = heiparse(file)
        doc_root = doc.getroot()
        if not doc_is_correspondence(doc_root):
            issues_in_CMIF_export.setdefault(file, []).append(
                "Document's type is not included in correspondence types; "
                "thus the file is not included in CMIF export.")
            continue

        correspondence_doi_elements = [idno for idno in doc_root.findall(".//tei:idno", namespaces=ns)
                                       if "hc:ReadingViewIdentifier" in idno.attrib["ana"]]
        if not correspondence_doi_elements:
            issues_in_CMIF_export.setdefault(file, []).append(
                "No ReadingViewIdentifier found. File is not included in CMIF export.")
            continue
        
        correspondence_doi = correspondence_doi_elements[0].text
        cmif_correspDesc = create_cmif_correspDesc(doc_root,
                                                   correspondence_doi,
                                                   edition_uuid,
                                                   file)
        if cmif_correspDesc is not None:
            cmif_profileDesc.append(cmif_correspDesc)

    write_xml_to_file(cmif_tree, output_path)
    print(issues_in_CMIF_export)
    return
