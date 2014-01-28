#!/usr/bin/python

import src.run.deploy
import src.run.backup
import argparse

def add_backup_args(parser):
    """
    Takes in an argparse parser and adds the options for the backup subcommand.
    This is necessary because of the way that argparse handles subparsers --
    namely, that they are created automatically at the time of addition.
    """
    parser.add_argument('-r','--recover',dest='recover',action='store_true',
        default=False,
        help='Boolean flag, indicates that recovery should be performed.')
    parser.add_argument('-s','--show-versions',dest='show_versions',
        action='store_true',default=False,
        help='Boolean flag, indicates that the file\'s versions should be '+\
        'displayed with varying generation numbers and dates.')
    parser.add_argument('-f','--filename',dest='filename',default=None,
        required=True,help='The absolute path to the file to act upon.')

    parser.set_defaults(func=src.run.backup.main)

def add_deploy_args(parser):
    """
    Takes in an argparse parser and adds the options for the deploy subcommand.
    This is necessary because of the way that argparse handles subparsers --
    namely, that they are created automatically at the time of addition.
    """
    parser.add_argument('-m','--manifest',dest='manifest',default=None,
        required=True,help='The root manifest file for execution.')
    parser.add_argument('-d','--directory',dest='directory',default=None,
        help='The directory to which relative paths in manifests refer.')

    parser.set_defaults(func=src.run.deploy.main)

def get_parser():
    """
    Produces a command line option parser for SALVE using argparse.
    Since we require python 2.7+, and 2.6 is not a target, we can move
    off of optparse.
    """
    class SALVESharedParser(argparse.ArgumentParser):
        def __init__(self, *args, **kwargs):
            argparse.ArgumentParser.__init__(self,*args,**kwargs)
            self.add_argument('-c','--config-file',dest='configfile',
                default=None,help='A SALVE config file.')

    parser = SALVESharedParser(description='Run SALVE.')

    subparsers = parser.add_subparsers(title='Subcommands',
        parser_class=SALVESharedParser,metavar='')

    backup_parser = subparsers.add_parser('backup',help='Directly manipulate'+\
        ', inspect, and restore from backups.')
    add_backup_args(backup_parser)

    deploy_parser = subparsers.add_parser('deploy',help='Run on a manifest'+\
        ' tree and deploy the described configuration.')
    add_deploy_args(deploy_parser)

    return parser
