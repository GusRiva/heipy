ns = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "xml": "http://www.w3.org/XML/1998/namespace",
    "hei": "https://digi.ub.uni-heidelberg.de/schema/tei/heiEDITIONS",
    "hc": "https://lod.ub.uni-heidelberg.de/ontologies/heieditions/hc/current/",
    "page": "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15",
    "mets": "http://www.loc.gov/METS/",
    "ex": "http://www.tei-c.org/ns/Examples",
    "xi": "http://www.w3.org/2001/XInclude"
}

def prefix_format(prefix, el):
    "Adds namespace to elment"
    return "{" + ns.get(prefix) + "}" + el

def ns_tags(namespace_uri, *local_names):
    """Convert local tag names to Clark notation"""
    return [f'{{{namespace_uri}}}{name}' for name in local_names]


class Namespace:
    """Namespace class that supports / operator for Clark notation.

    Usage:
        from heipy.namespaces import tei_ns
        element_tag = tei / "lg"  # Returns "{http://www.tei-c.org/ns/1.0}lg"
    """

    def __init__(self, uri):
        self.uri = uri

    def __truediv__(self, element_name):
        """Overload / operator to create Clark notation."""
        return f"{{{self.uri}}}{element_name}"

    def __repr__(self):
        return f"Namespace('{self.uri}')"


# Create namespace instances for convenient usage
tei_ns = Namespace(ns["tei"])
xml_ns = Namespace(ns["xml"])
hei_ns = Namespace(ns["hei"])
hc_ns = Namespace(ns["hc"])
page_ns = Namespace(ns["page"])
mets_ns = Namespace(ns["mets"])
ex_ns = Namespace(ns["ex"])
xi_ns = Namespace(ns["xi"])

