import argparse

def get_cli_parser():
    parser = argparse.ArgumentParser(
        description="Shared argument parser for my scripts"
    )

    parser.add_argument("text_files", nargs="*", help="List of input files")

    parser.add_argument("--semantic", '-sem', action="store_true",  help="Semantic pipeline")
    parser.add_argument("--synoptic", '-syn', action="store_true", help="Synoptic pipeline")
    parser.add_argument("--sourcedoc", '-sou', action="store_true", help="SourceDoc pipeline", required=False)

    return parser