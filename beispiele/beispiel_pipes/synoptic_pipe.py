import argparse
import os 
import codecs

from src.heipy.heipipe.steps import Pipeline, DeleteStep
from src.heipy.heipipe.step_library import create_synoptic_wit, resolve_semantic_logical_elements_to_milestones, whitespaces

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-i', '--input', required=True, help="i: path to the input document",
                        dest="input")
arg_parser.add_argument('-o', '--output', required=True,
                        help="o: path to the output file", dest="output")
arg_parser.add_argument('-smap', '--synoptic-map', required=True,
                        help="smap: path to the synoptic map", dest="smap")
args = arg_parser.parse_args()
input_file = args.input
output_file_path = args.output
synoptic_map_path = args.smap

pipe_synoptic = Pipeline()
pipe_synoptic.add_step(whitespaces.get_step(), serial=True)
pipe_synoptic.add_step(DeleteStep(['facsimile']))
pipe_synoptic.add_step(resolve_semantic_logical_elements_to_milestones.get_step())
pipe_synoptic.add_step(create_synoptic_wit.get_step(), 
                       parameters={'synoptic_map': synoptic_map_path,
                                   'base_file_name': os.path.basename(input_file)})





result = pipe_synoptic.execute(input_file)
output_file = codecs.open(output_file_path, "w", "utf-8")
output_file.write(result)

