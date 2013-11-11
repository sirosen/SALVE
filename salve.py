#!/usr/bin/python

from __future__ import print_function
import os, optparse, sys

import src.util.locations as locations
import src.execute.block as block
from src.settings.config import SALVEConfig

def get_option_parser():
    option_parser = optparse.OptionParser()
    option_parser.add_option('-m','--manifest',dest='manifest',
                             help='The root manifest for execution.')
    option_parser.add_option('--git-repo',dest='gitrepo',
                             help='A SALVE git repo, '+\
                             'containing a root.manifest in HEAD.')
    option_parser.add_option('-c','--config-file',dest='configfile',
                             help='A SALVE config file.')
    return option_parser

if __name__ == '__main__':
    option_parser = get_option_parser()
    (opts,args) = option_parser.parse_args()

    if not opts.manifest and not opts.gitrepo:
        raise KeyError('The present version of SALVE must be invoked '+\
                       'with a manifest or git repo.')

    if opts.gitrepo and opts.manifest:
        print('Ambiguous arguments: given a git repo and a manifest'+\
              ' and therefore choosing the manifest.',
              file=sys.stderr)

    cfg_file = None
    if opts.configfile:
        cfg_file = opts.configfile
    conf = SALVEConfig(filename=cfg_file)

    root_manifest = None
    if opts.manifest:
        root_manifest = opts.manifest
    elif opts.gitrepo:
        raise StandardError('TODO: clone git repo; set root_manifest')

    root_block = block.ManifestBlock(source=root_manifest)
    root_block.expand_blocks(conf)
    root_action = root_block.to_action()
    root_action.execute()
