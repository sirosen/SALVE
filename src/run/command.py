#!/usr/bin/python

from __future__ import print_function
import os, optparse, sys

import src.util.locations as locations
import src.block.manifest_block
from src.settings.config import SALVEConfig

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
    option_parser.add_option('--file-root',dest='fileroot',
                             help='The directory to which relative'+\
                             'paths in manifests refer.')
    option_parser.add_option('-c','--config-file',dest='configfile',
                             help='A SALVE config file.')
    return option_parser

def read_commandline(option_parser=None):
    """
    Reads the commandline with a SALVE option parser, and validates the
    inputs that were received.
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
    """
    cfg_file = None
    if opts.configfile:
        cfg_file = opts.configfile
    conf = SALVEConfig(filename=cfg_file)

    root_block = src.block.manifest_block.ManifestBlock(source=root_manifest)
    root_block.expand_blocks(conf)
    root_block.expand_file_paths(root_dir=opts.fileroot)
    root_action = root_block.to_action()
    root_action.execute()

def get_root_manifest(opts):
    """
    Given a set of options, identifies the root manifest that they
    describe.
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

    run_on_manifest(get_root_manifest(opts),opts)
