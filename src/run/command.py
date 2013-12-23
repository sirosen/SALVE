#!/usr/bin/python

from __future__ import print_function

import os
import sys
import optparse

import src.util.locations as locations
import src.block.manifest_block
from src.settings.config import SALVEConfig
from src.util.error import SALVEException

def get_option_parser():
    """
    Produces a command line option parser for SALVE using optparse.
    Although argparse is significantly nicer, it's only available as
    an added package in python<2.7. Since 2.6 is in wide use at this
    time, optparse is going to have to do.
    """
    option_parser = optparse.OptionParser()
    option_parser.add_option('-m','--manifest',dest='manifest',
                             help='The root manifest for execution.')
    option_parser.add_option('--git-repo',dest='gitrepo',
                             help='A SALVE git repo, '+\
                             'containing a root.manifest in HEAD.')
    option_parser.add_option('--fileroot',dest='fileroot',
                             help='The directory to which relative'+\
                             'paths in manifests refer.')
    option_parser.add_option('-c','--config-file',dest='configfile',
                             help='A SALVE config file.')
    return option_parser

def read_commandline(option_parser=None):
    """
    Reads the commandline with a SALVE option parser, and validates the
    inputs that were received.

    KWArgs:
        @option_parser
        A given option_parser for reading the commandline. If not given,
        or given as a non-true value, the function will generate a new
        one.
    """
    if not option_parser:
        option_parser = get_option_parser()

    (opts,args) = option_parser.parse_args()

    if not opts.manifest and not opts.gitrepo:
        raise KeyError('The present version of SALVE must be invoked '+\
                       'with a manifest or git repo.')

    if opts.gitrepo and opts.manifest:
        print('Ambiguous arguments: given a git repo and a manifest'+\
              ' and therefore choosing the manifest.',
              file=sys.stderr)

    return (opts,args)

def run_on_manifest(root_manifest,opts):
    """
    Given a manifest file, loads SALVEConfig, parses and expands the
    root manifest, then executes the actions defined by that manifest.

    Args:
        @root_manifest
        The manifest at the root of the manifest tree, and starting
        point for manifest execution.
        @opts
        The options, as parsed from the commandline.
    """
    cfg_file = None
    if opts.configfile: cfg_file = opts.configfile
    conf = SALVEConfig(filename=cfg_file)

    root_dir = locations.get_salve_root()
    if opts.fileroot: root_dir = os.path.abspath(opts.fileroot)

    # root_block is a synthetic manifest block containing the root
    # manifest
    root_block = src.block.manifest_block.ManifestBlock(source=root_manifest)
    root_block.expand_blocks(root_dir,conf)

    root_action = root_block.to_action()
    root_action()

def get_root_manifest(opts):
    """
    Given a set of options, identifies the root manifest that they
    describe.

    Args:
        @opts
        Options, as parsed from the commandline.
    """
    root_manifest = None
    if opts.manifest:
        root_manifest = opts.manifest
    elif opts.gitrepo:
        raise StandardError('TODO: clone git repo; set root_manifest')
    return root_manifest

def main():
    """
    The main method of the entire SALVE codebase. Runs the entire
    program end-to-end.
    """
    opts,args = read_commandline()

    try:
        run_on_manifest(get_root_manifest(opts),opts)
    except SALVEException as e:
        print(e.to_message(),file=sys.stderr)
        # Normally, sys.exit() is to be avoided, but main() is only
        # invoked if salve is running as a script, and we want to give
        # the right exit status for commandline usage
        sys.exit(1)
    except: raise
