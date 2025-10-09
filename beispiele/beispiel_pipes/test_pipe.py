import argparse
import codecs

from heipy.heipipe.pipeline_library.synoptic import HeiCritPipe

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument('-i', '--input', required=True, help="i: path to the input document",
                        dest="input")
arg_parser.add_argument('-o', '--output', required=True,
                        help="o: path to the output file", dest="output")

args = arg_parser.parse_args()
input_file = args.input
output_file_path = args.output

pipe_synoptic = HeiCritPipe()


result = pipe_synoptic.execute(input_file)
output_file = codecs.open(output_file_path, "w", "utf-8")
output_file.write(result)
