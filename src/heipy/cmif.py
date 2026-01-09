import datetime
import hashlib
import sys
import warnings
import importlib.resources
import json
import uuid
from pathlib import Path
from lxml import etree as et

from .namespaces import ns, prefix_format
from .parsers import heiparse

issues_in_CMIF_export = {}


def element_exists_in_parent(parent: et.Element, tag: str, text_value: str, ref_value: str = None) -> bool:
    """
    Checks if an element with name *tag* exists in *parent*. If yes, @ref=*ref_value* is compared between them;
    if no *ref_value* is given, a string comparison of *text_value* between them is used instead.
    This function is used to prevent the addition of duplicates.
    """
    xpath = f"./{tag}"
    existing_elements = parent.findall(xpath, namespaces=ns)
    if not existing_elements:
        return False
    for element in existing_elements:
        if ref_value:
            if element.get('ref') == ref_value:
                return True
        else:
            if element.text == text_value:
                return True
    return False


def add_cmif_persName_to_correspAction(correspAction: et.Element, cmif_correspAction: et.Element):
    # if our guidelines are changed and multiple persNames can be stored in a single correspAction, adjust here
    persName_element = correspAction.find(".//tei:persName", namespaces=ns)
    if persName_element is None:
        return

    persName_str = persName_element.text
    persName_parent = correspAction.find(".//tei:persName", namespaces=ns).getparent()
    persName_idno_element = persName_parent.find(".//tei:idno[@ana='hc:GNDURI']", namespaces=ns)
    persName_idno_str = persName_idno_element.text if persName_idno_element is not None else None

    if element_exists_in_parent(cmif_correspAction, "persName", persName_str, persName_idno_str):
        return

    cmif_persName = et.SubElement(cmif_correspAction, "persName")
    cmif_persName.text = persName_str

    if persName_idno_str is not None:
        cmif_persName.set("ref", persName_idno_str)
    return


def add_cmif_placeName_to_correspAction(correspAction: et.Element,
                                        cmif_correspAction: et.Element,
                                        filename: str):
    for place_info in correspAction.findall("./tei:location", namespaces=ns):
        placeName_element = place_info.find("./tei:placeName", namespaces=ns)
        if placeName_element is None:
            continue
        placeName_str = placeName_element.text
        geonames_idno_element = place_info.find("./tei:idno[@ana = 'hc:GeonamesURI']", namespaces=ns)
        geonames_idno_str = geonames_idno_element.text if geonames_idno_element is not None else None

        if element_exists_in_parent(cmif_correspAction, "placeName", placeName_str, geonames_idno_str):
            continue

        cmif_placeName = et.SubElement(cmif_correspAction, "placeName")
        cmif_placeName.text = placeName_str
        if geonames_idno_str:
            cmif_placeName.set("ref", geonames_idno_str)
        else:
            message = f"Included {placeName_str} without Geonames-ID."
            issues_in_CMIF_export.setdefault(filename, []).append(message)
    return


def add_cmif_date_to_correspAction(correspAction: et.Element, cmif_correspAction: et.Element):
    date_elements: list = correspAction.findall("./tei:date", namespaces=ns)
    if not date_elements:
        return
    if len(date_elements) > 1:
        warnings.warn("More than one date element in a single correspAction.")
    date = date_elements[0]
    cmif_date = cmif_correspAction.find(".//date", namespaces=ns)  # should always only be one

    # no date entries in correspAction, yet: add date
    if cmif_date is None:
        cmif_date = et.SubElement(cmif_correspAction, "date")
        for attr, val in date.attrib.items():
            cmif_date.set(attr, val)
        return

    # handling in case of duplicates (CMIF: multiple correspActions of the same type must be combined into a single one)
    date_attrs = sorted(date.items())
    cmif_date_attrs = sorted(cmif_date.items())

    # date is already included in cmif entry
    if date_attrs == cmif_date_attrs:
        return

    # cmif date entry does not contain this date, but other attributes:
    combined_attrs = cmif_date_attrs + date_attrs
    unresolved_date_attrs = ["notBefore", "notAfter", "notBefore-iso",
                             "notAfter-iso"]  # waiting for examples before implementing
    resolved_date_attrs = ["from", "to", "when", "when-iso", "from-iso", "to-iso"]
    all_dates = []
    cert_order = {'high': 1, 'medium': 2, 'low': 3}
    cert_value = 0
    for attr, val in combined_attrs:
        if attr in unresolved_date_attrs:
            warnings.warn(f"Unresolved date attribute in correspAction: {attr}: {val}")
            sys.exit(1)
        elif attr in resolved_date_attrs:
            all_dates.append(val)
        elif attr == "cert":  # set the lowest certainty value used if multiple ones were found in the correspAction's dates
            if cert_order.get(val) > cert_value:
                cert_value = cert_order[val]
                cmif_date.set("cert", val)

    if all_dates:
        all_dates.sort()  # Sonderfälle wie <date when="--12-12"> ergänzen, in WM nicht enthalten
        if len(set(all_dates)) == 1:
            cmif_date.set("when", all_dates[0])
        else:
            cmif_date.set('from', all_dates[0])
            cmif_date.set('to', all_dates[-1])
            if "when" in cmif_date.attrib:
                del cmif_date.attrib['when']
    return


def create_cmif_correspActions(correspActions: list[et.Element], cmif_correspDesc: et.Element, filename: str) -> None:
    sent_actions, received_actions = extract_correspActions_by_type(correspActions, filename)
    cmif_sent_action = combine_correspActions_of_single_type_to_cmif_correspAction(sent_actions, "sent", filename)
    cmif_received_action = combine_correspActions_of_single_type_to_cmif_correspAction(received_actions, "received",
                                                                                       filename)
    cmif_correspDesc.append(cmif_sent_action)
    cmif_correspDesc.append(cmif_received_action)
    return


def extract_correspActions_by_type(correspActions: list[et.Element], filename: str) -> tuple[
    list[et.Element], list[et.Element]]:
    send_types = ["hc:CorrespondenceAuthoring", "hc:CorrespondenceSending"]
    receive_types = ["hc:DesignationAsCorrespondenceAddressee", "hc:CorrespondenceReceiving"]

    sent_actions = [ca for ca in correspActions if ca.attrib.get("ana") in send_types]
    received_actions = [ca for ca in correspActions if ca.attrib.get("ana") in receive_types]
    other_actions = [ca for ca in correspActions if
                     ca.attrib.get("ana") not in send_types and ca.attrib.get("ana") not in receive_types]
    if other_actions:
        print(f"{filename} contains correspAction-types that have not been mapped to a CMIF type (allowed: 'sent' or "
              f"'received'), yet or it has no correspAction-types. Please correct this and update the mapping.")
    return sent_actions, received_actions


def create_cmif_correspDesc(doc: et.Element, ref: str, edition_uuid: str, filename: str) -> et.Element:
    cmif_correspDesc = et.Element("correspDesc", ref=ref,
                                  source='#' + edition_uuid)  # key=filename[:-4]: Stefan Dumont: nur für richtige Nummerierung wie in gedruckten Editionen intendiert
    correspDescs = doc.findall(".//tei:correspDesc", namespaces=ns)
    if not correspDescs:
        issues_in_CMIF_export.setdefault(filename, []).append("No correspDesc-element found. Skipped for CMIF export.")
        return None

    correspActions = [correspAction for correspDesc in correspDescs for correspAction in
                      correspDesc.findall(".//tei:correspAction", namespaces=ns)]
    create_cmif_correspActions(correspActions, cmif_correspDesc, filename)

    return cmif_correspDesc


def combine_correspActions_of_single_type_to_cmif_correspAction(actions, action_type, filename):
    cmif_correspAction = et.Element("correspAction")
    cmif_correspAction.set("type", action_type)

    if not actions:
        pers_name = et.SubElement(cmif_correspAction, "persName")
        pers_name.text = "Unbekannt"
        return cmif_correspAction

    for action in actions:
        add_cmif_persName_to_correspAction(action, cmif_correspAction)
        add_cmif_placeName_to_correspAction(action, cmif_correspAction, filename)
        add_cmif_date_to_correspAction(action, cmif_correspAction)

    return cmif_correspAction


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
    if id[0].isnumeric():  # would lead to an invalid XML id
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
    edition_citation_element = et.fromstring(f'<temp_wrapper_tag>{edition_citation}</temp_wrapper_tag>')
    bibl.text = edition_citation_element.text
    for child in edition_citation_element:
        bibl.append(child)

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
                            "hc:Telegram"]  # envelope nicht (nur an div)
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
                "Document's type is not included in correspondence types. "
                "File is not included in CMIF export.")
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

    sort_container = cmif_tree.find(".//tei:profileDesc", namespaces=ns)
    sort_container[:] = sorted(sort_container, key=lambda el: el.get("ref"))
    write_xml_to_file(cmif_tree, output_path)
    sorted_issues_in_CMIF_export_json = json.dumps(dict(sorted(issues_in_CMIF_export.items())))
    print(sorted_issues_in_CMIF_export_json)
    return
