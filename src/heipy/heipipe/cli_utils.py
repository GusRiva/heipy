import argparse


class HeipyCliArgumentParser(argparse.ArgumentParser):
    def parse_args(self, args=None, namespace=None):        
        parsed_args = super().parse_args(args, namespace)
        
        # Possible flags
        flags = ["semantic", "sourcedoc", "synoptic"]
        if not any(getattr(parsed_args, flag) for flag in flags):
            for flag in flags:
                setattr(parsed_args, flag, True)
            
        return parsed_args


def get_cli_parser():
    parser = HeipyCliArgumentParser(
        description="Shared argument parser for my scripts"
    )

    parser.add_argument("text_files", nargs="*", help="List of input files")

    parser.add_argument("--semantic", '-sem', action="store_true",  help="Semantic pipeline")
    parser.add_argument("--synoptic", '-syn', action="store_true", help="Synoptic pipeline")
    parser.add_argument("--sourcedoc", '-sou', action="store_true", help="SourceDoc pipeline", required=False)

    return parser



