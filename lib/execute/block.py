#!/usr/bin/python

import abc

from lib.util.enum import Enum
from lib.parse.tokenize import Token
import lib.parse.parse
import lib.execute.action as action

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
        raise action.ActionException('TODO')

class ManifestBlock(Block):
    """
    A manifest block describes another manifest to be expanded and
    executed. It may also specify properties of that manifest's
    execution. For example, if a manifest's blocks can be executed
    in parallel, or if its execution is conditional on a file existing.
    """
    def __init__(self):
        Block.__init__(self,Block.types.MANIFEST)

    def to_action(self):
        filename = self.attrs['source']
        with open(filename) as man:
            blocks = lib.parse.parse.parse_stream(man)
            return action.ActionList([b.to_action() for b in blocks])

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
