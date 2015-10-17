import sys

from .parser import load_args


def run():
    """
    Reads the commandline with a SALVE argument parser, and runs the function
    designated by the arguments.
    """
    args = load_args()

    args.func(args)


def main():
    if sys.version_info < (2, 6):
        sys.exit('Python Version Too Old! SALVE Requires Python >= 2.6')

    run()
