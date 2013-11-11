#!/usr/bin/python

import abc, os

from src.util.enum import Enum
from src.reader.tokenize import Token

import src.reader.parse as parse
import src.execute.action as action
import src.util.locations as locations

class BlockException(StandardError):
    """
    An exception specialized for blocks.
    """
    def __init__(self,msg):
        StandardError.__init__(self,msg)
        self.message = msg

class Block(object):
    """
    A block is the basic unit of configuration.
    Typically, blocks describe files, SALVE manifests, patches, etc
    """
    __metaclass__ = abc.ABCMeta

    types = Enum('FILE','MANIFEST')
    def __init__(self,ty):
        self.block_type = ty
        self.attrs = {}

    def add_attribute(self,attribute_name,value):
        self.attrs[attribute_name] = value

    @abc.abstractmethod
    def to_action(self): return

    @abc.abstractmethod
    def expand_file_paths(self, root_dir=None): return

class FileBlock(Block):
    """
    A file block describes an action performed on a file.
    This includes creation, deletion, and string append.
    """
    def __init__(self):
        Block.__init__(self,Block.types.FILE)

    def expand_file_paths(self,root_dir=None):
        """
        Expand relative paths in source and target to be absolute paths
        beginning with the SALVE_ROOT.
        """
        if 'source' not in self.attrs or 'target' not in self.attrs:
            # TODO: replace with a more informative exception
            raise BlockException('FileBlock missing source and target')

        if not root_dir: root_dir = locations.get_salve_root()
        if not locations.is_abs_or_var(self.attrs['source']):
            self.attrs['source'] = os.path.join(root_dir,
                                                self.attrs['source'])
        if not locations.is_abs_or_var(self.attrs['target']):
            self.attrs['target'] = os.path.join(root_dir,
                                                self.attrs['target'])

    def to_action(self):
        # is a no-op if it has already been done
        # otherwise, it ensures that everything will work
        self.expand_file_paths()
        if self.attrs['action'] == 'create':
            # TODO: replace asserts with a check & exception,
            # preferably wrapped in a function of some kind
            assert 'source' in self.attrs
            assert 'target' in self.attrs
            assert 'user' in self.attrs
            assert 'group' in self.attrs
            assert 'mode' in self.attrs
            copy_file = ' '.join(['cp',
                                  self.attrs['source'],
                                  self.attrs['target']
                                 ])
            chown_file = ' '.join(['chown',
                                   self.attrs['user']+':'+\
                                   self.attrs['group'],
                                   self.attrs['target']
                                  ])
            chmod_file = ' '.join(['chmod',
                                   self.attrs['mode'],
                                   self.attrs['target']
                                  ])
            return action.ShellAction([copy_file,chown_file,chmod_file])
        else:
            raise action.ActionException('Unsupported file block action.')

class ManifestBlock(Block):
    """
    A manifest block describes another manifest to be expanded and
    executed. It may also specify properties of that manifest's
    execution. For example, if a manifest's blocks can be executed
    in parallel, or if its execution is conditional on a file existing.
    """
    def __init__(self,source=None):
        Block.__init__(self,Block.types.MANIFEST)
        self.sub_blocks = None
        if source:
            self.attrs['source'] = source

    def expand_blocks(self,config,recursive=True,ancestors=None,root_dir=None):
        assert 'source' in self.attrs
        if not ancestors:
            ancestors = set()
        filename = self.attrs['source']

        if filename in ancestors:
            raise BlockException('Manifest ' + filename +\
                                 ' includes itself')

        ancestors.add(filename)
        with open(filename) as man:
            self.sub_blocks = parse.parse_stream(man)
        for b in self.sub_blocks:
            b.expand_file_paths(root_dir=root_dir)
            config.apply_to_block(b)
            if recursive and isinstance(b,ManifestBlock):
                b.expand_blocks(config,ancestors=ancestors,root_dir=root_dir)

    def expand_file_paths(self,root_dir=None):
        assert 'source' in self.attrs

        if not locations.is_abs_or_var(self.attrs['source']):
            if not root_dir: root_dir = locations.get_salve_root()
            self.attrs['source'] = os.path.join(root_dir,
                                                self.attrs['source'])

    def to_action(self):
        assert self.sub_blocks is not None
        return action.ActionList([b.to_action()
                                  for b in self.sub_blocks])

# maps valid identifiers to block constructors
Block.identifier_map = {
    'file': FileBlock,
    'manifest': ManifestBlock
}

def block_from_identifier(id_token):
    """
    Given an identifier, constructs a block of the appropriate
    type and returns it.
    Fails if the identifier is unknown, or the token given is
    not an identifier.
    """
    assert id_token.ty == Token.types.IDENTIFIER
    val = id_token.value.lower()
    try:
        return Block.identifier_map[val]()
    except KeyError:
        raise ValueError('Unknown block identifier ' + val)
