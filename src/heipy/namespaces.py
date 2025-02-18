ns = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace",
    "hei": "https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS",
    "hc": "https://lod.ub.uni-heidelberg.de/ontologies/heieditions/hc/current/",
    "page": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15",
    "mets": "http://www.loc.gov/METS/"
}

def prefix_format(prefix, el):
    "Adds namespace to elment"
    return "{" + ns.get(prefix) + "}" + el
