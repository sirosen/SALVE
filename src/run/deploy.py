#!/usr/bin/python

from __future__ import print_function

import os
import sys

import src.util.locations as locations
import src.block.manifest_block

import src.settings.config as config
from src.util.enum import Enum
from src.util.error import SALVEException

def run_on_manifest(root_manifest,args):
    """
    Given a manifest file, loads SALVEConfig, parses and expands the
    root manifest, then executes the actions defined by that manifest.

    Args:
        @root_manifest
        The manifest at the root of the manifest tree, and starting
        point for manifest execution.
        @args
        The options, as parsed from the commandline.
    """
    cfg_file = None
    if args.configfile: cfg_file = args.configfile
    conf = config.SALVEConfig(filename=cfg_file)

    root_dir = locations.get_salve_root()
    if args.directory: root_dir = os.path.abspath(args.directory)

    # root_block is a synthetic manifest block containing the root
    # manifest
    root_block = src.block.manifest_block.ManifestBlock(source=root_manifest)
    root_block.expand_blocks(root_dir,conf)

    root_action = root_block.to_action()
    root_action()

def main(args):
    """
    The main method of SALVE deployment. Runs the core program end-to-end.
    """
    try:
        assert args.manifest
        run_on_manifest(args.manifest,args)
    except SALVEException as e:
        print(e.to_message(),file=sys.stderr)
        # Normally, sys.exit() is to be avoided, but main() is only
        # invoked if salve is running as a script, and we want to give
        # the right exit status for commandline usage
        sys.exit(1)
    except: raise
