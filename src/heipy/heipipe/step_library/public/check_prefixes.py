from ...steps import PythonStep
from lxml import etree as et
from ....namespaces import ns, tei_ns


def check_prefixes_func(tree, parameters=None):
    tei_header = tree.xpath("//tei:teiHeader", namespaces=ns)[0]
    encoding_desc = tei_header.find("tei:encodingDesc", namespaces=ns)

    if encoding_desc is None:
        encoding_desc = et.SubElement(tei_header, tei_ns / "encodingDesc")

    list_prefix_def = encoding_desc.find("tei:listPrefixDef", namespaces=ns)
    if list_prefix_def is None:
        list_prefix_def = et.SubElement(encoding_desc, tei_ns / "listPrefixDef")

    if not list_prefix_def.xpath("tei:prefixDef[@ident=('hc')]", namespaces=ns):
        et.SubElement(list_prefix_def, tei_ns / "prefixDef", attrib={"ident": "hc",
                                                                  "matchPattern": "(.+)",
                                                                  "replacementPattern": "https://lod.ub.uni-heidelberg.de/ontologies/heieditions/hc/current/$1" }
                      )
    if not list_prefix_def.xpath("tei:prefixDef[@ident=('char')]", namespaces=ns):
        et.SubElement(list_prefix_def, tei_ns / "prefixDef", attrib={"ident": "char",
                                                                  "matchPattern": "(.+)",
                                                                  "replacementPattern": "https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS/declarations/chars.xml#$1" }
                      )
    return tree

def get_step():
    return PythonStep(check_prefixes_func, name="check_prefixes")
