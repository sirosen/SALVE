#!/usr/bin/python

from __future__ import print_function

import os
import sys

import salve

from salve import paths
from salve.config import SALVEConfig
from salve.context import FileContext, ExecutionContext
from salve.exceptions import SALVEException
from salve.block import ManifestBlock
from salve.filesys import ConcreteFilesys


def run_on_manifest(root_manifest, args):
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
    if args.configfile:
        cfg_file = args.configfile
    conf = SALVEConfig(filename=cfg_file)

    # must be done after config is loaded to have correct override behavior
    if args.verbosity:
        ExecutionContext().set('verbosity', args.verbosity)

    root_dir = paths.containing_dir(root_manifest)
    if args.directory and not args.v3_relpath:
        root_dir = os.path.abspath(args.directory)

    # root_block is a synthetic manifest block containing the root
    # manifest
    root_block = ManifestBlock(FileContext('no such file'),
                               source=root_manifest)
    root_block.expand_blocks(root_dir, conf, args.v3_relpath)

    root_action = root_block.compile()
    root_action(ConcreteFilesys())


def clean_and_validate_args(args):
    """
    Takes commandline arguments as parsed by argparse, and tidies them up.
    Does higher level validation, rewrites to special values, warns about
    option deprecations, and may raise exceptions if things look _very_ wrong
    (i.e. agparse didn't keep us safe).
    Doesn't return anything, but may modify the args object.

    Args:
        @args
        `salve deploy` arguments parsed by argparse
    """
    # assert that argparse did minimal validation
    assert args.manifest

    # set all v3 options if version3 is set
    if args.version3:
        args.v3_relpath = True

    # warn about deprecations coming in v3
    if args.directory:
        salve.logger.warn(
            'Deprecation Warning: --directory will be ' +
            'removed in version 3 as --version3-relative-paths becomes the ' +
            'default.')


def main(args):
    """
    The main method of SALVE deployment. Runs the core program end-to-end.
    """
    clean_and_validate_args(args)

    try:
        run_on_manifest(args.manifest, args)
    except SALVEException as e:
        salve.logger.error(str(e.file_context) + ': ' + e.message)
        # Normally, sys.exit() is to be avoided, but main() is only
        # invoked if salve is running as a script, and we want to give
        # the right exit status for commandline usage
        sys.exit(1)
