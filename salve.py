#!/usr/bin/python

"""
Import the main function and run it.

This should do the following:
- Parse commandline arguments
- Load configuration from ini files
- Create an ephemeral Manifest Block pointing at the root Manifest
- Convert the root Manifest Block to an Action and execute it
"""

import sys

if sys.version_info < (2, 6):
    sys.exit(1)

from salve.run.command import run
run()
