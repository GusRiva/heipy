import argparse


class HeipyCliArgumentParser(argparse.ArgumentParser):
    def parse_args(self, args=None, namespace=None):        
        parsed_args = super().parse_args(args, namespace)
        
        # Possible flags
        flags = ["semantic", "sourcedoc", "synoptic"]
        if not any(getattr(parsed_args, flag) for flag in flags):
            for flag in flags:
                setattr(parsed_args, flag, True)

        if parsed_args.debug is not None:  
            if len(parsed_args.debug) == 0: 
                parsed_args.debug = ['time', 'serial']
            
        return parsed_args


def get_cli_parser():
    parser = HeipyCliArgumentParser(
        description="Shared argument parser for my scripts",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("text_files", nargs="*", help="List of input files")

    parser.add_argument("--semantic", '-sem', action="store_true",  help="Semantic pipeline")
    parser.add_argument("--synoptic", '-syn', action="store_true", help="Synoptic pipeline")
    parser.add_argument("--sourcedoc", '-sou', action="store_true", help="SourceDoc pipeline", required=False)

    parser.add_argument("--debug",
                        nargs='*',
                        choices=['time', 'serial'],
                        metavar='OPTION',
                        help='''Enable debug options. Use without arguments for all options.
Available options:
    • time    - Show execution time for functions.
    • serial  - Serialize the result of each step into a file to be stored in the tmp directory.''')



    return parser



