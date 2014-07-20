#!/usr/bin/python

from __future__ import print_function

import os
import sys

import salve

import salve.util.locations as locations
import salve.block.manifest_block

import salve.settings.config as config
from salve.util.enum import Enum
from salve.util.context import SALVEContext, ExecutionContext
from salve.util.error import SALVEException


def run_on_manifest(root_manifest, args):
    """
    Given a manifest file, loads SALVEConfig, parses and expands the
    root manifest, then executes the actions defined by that manifest.

    Args:
        @root_manifest
        The manifest at the root of the manifest tree, and starting
        point for manifest execution.
        @context
        The SALVEContext containing execution context. Does not include
        a StreamContext, as that is not yet relevant.
        @args
        The options, as parsed from the commandline.
    """
    context = SALVEContext(exec_context=salve.exec_context)
    cfg_file = None
    if args.configfile:
        cfg_file = args.configfile
    conf = config.SALVEConfig(context, filename=cfg_file)

    # must be done after config is loaded to have correct override behavior
    if args.verbosity:
        context.exec_context.set('verbosity', args.verbosity)

    root_dir = locations.get_salve_root()
    if args.directory:
        root_dir = os.path.abspath(args.directory)

    # root_block is a synthetic manifest block containing the root
    # manifest
    root_block = salve.block.manifest_block.ManifestBlock(context,
            source=root_manifest)
    root_block.expand_blocks(root_dir, conf)

    root_action = root_block.compile()
    root_action()


def main(args):
    """
    The main method of SALVE deployment. Runs the core program end-to-end.
    """
    try:
        assert args.manifest
        run_on_manifest(args.manifest, args)
    except SALVEException as e:
        salve.logger.error(e.message, file_context=e.context.stream_context)
        # Normally, sys.exit() is to be avoided, but main() is only
        # invoked if salve is running as a script, and we want to give
        # the right exit status for commandline usage
        sys.exit(1)
    except:
        raise
