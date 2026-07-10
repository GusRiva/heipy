from ...steps import PythonStep
from ....namespaces import ns

def change_ref(tree, parameters):
    root = tree.getroot()
    if isinstance(parameters, list):
        if len(parameters) > 0:
            parameters = parameters[0]
    mapping = parameters.get('mapping') if 'mapping' in parameters else None

    if mapping is None:
        print("ERROR: Please supply a configuration file (parameter 'mapping') for the synoptic map pipeline.")
        return tree
    prefix_siglum_dict = {}
    for key, v in mapping.items():
        if 'synoptic_pre' in v and 'siglum' in v:
            prefix_siglum_dict[v['synoptic_pre']] = v['siglum']
        else:
            print(f"Warning: Missing 'synoptic_pre' or 'siglum' in {key}")
    for prefixDef in root.findall('.//tei:prefixDef', ns):
        if prefixDef.get('ana') != 'hc:SynopticTextPrefixDefinition':
            continue
        ident = prefixDef.get('ident')
        siglum = prefix_siglum_dict.get(ident)
        if siglum is None:
            print(f"WARNING: Could not find siglum for prefix {ident} in synoptic map.")
            continue
        prefixDef.set('replacementPattern', f"{siglum}/{siglum}.xml")


    return tree

def get_step():
    return PythonStep(change_ref, name= "change_prefixdef_ref_synopticmap")

