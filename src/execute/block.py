#!/usr/bin/python

import abc

from src.util.enum import Enum
from src.reader.tokenize import Token
import src.reader.parse
import src.execute.action as action

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

class FileBlock(Block):
    """
    A file block describes an action performed on a file.
    This includes creation, deletion, and string append.
    """
    def __init__(self):
        Block.__init__(self,Block.types.FILE)

    def to_action(self):
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

    def expand_blocks(self,config,recursive=True,ancestors=None):
        assert 'source' in self.attrs
        if not ancestors:
            ancestors = set()
        filename = self.attrs['source']

        if filename in ancestors:
            raise BlockException('Manifest ' + filename +\
                                 ' includes itself')

        ancestors.add(filename)
        with open(filename) as man:
            self.sub_blocks = src.reader.parse.parse_stream(man)
        for b in self.sub_blocks:
            config.apply_to_block(b)
            if recursive and isinstance(b,ManifestBlock):
                b.expand_blocks(config,ancestors=ancestors)

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
