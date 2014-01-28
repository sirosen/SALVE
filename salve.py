#!/usr/bin/python

"""
Import the main function and run it.

This should do the following:
- Parse commandline arguments
- Load configuration from ini files
- Create an ephemeral Manifest Block pointing at the root Manifest
- Convert the root Manifest Block to an Action and execute it
"""

from src.run.command import run
run()
