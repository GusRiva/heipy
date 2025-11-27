from .parsers import heiparse
from .namespaces import ns
from pathlib import Path

def create_configuration_json(input_files:list)->dict:
    output_dict = {}
    for file_name in input_files:
        file_dict = {}
        file_path = Path(file_name)
        if not file_path.exists():
            print(f"There is an error, can not find file {file_path}")
            continue
        input_tree = heiparse(file_path)
        siglum_el = input_tree.find('.//tei:idno[@ana="hc:EditorialSiglum"]', ns)
        siglum = ''
        if siglum_el is None:
            print(f"No siglum defined for {file_path}. Use idno with @ana='hc:EditorialSiglum' in the witness description.")
        else:
            siglum = siglum_el.text
        file_dict['siglum'] = siglum
        
        output_dict[file_name] = file_dict

    return