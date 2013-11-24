#!/usr/bin/python

import abc

from src.util.enum import Enum
from src.util.error import SALVEException

class BlockException(SALVEException):
    """
    An exception specialized for blocks.
    """
    def __init__(self,msg,context):
        SALVEException.__init__(self,msg,context)

class Block(object):
    """
    A block is the basic unit of configuration.
    Typically, blocks describe files, SALVE manifests, patches, etc
    """
    __metaclass__ = abc.ABCMeta

    types = Enum('FILE','MANIFEST','DIRECTORY')
    def __init__(self,ty,exception_context):
        self.block_type = ty
        self.context = exception_context
        self.attrs = {}

    def set(self,attribute_name,value):
        self.attrs[attribute_name] = value

    def get(self,attribute_name):
        return self.attrs[attribute_name]

    def has(self,attribute_name):
        return attribute_name in self.attrs

    def ensure_has_attrs(self,*args):
        for attr in args:
            if not self.has(attr):
                raise self.make_exception('Block(ty='+self.block_type+') '+\
                                          'missing attr "'+attr+'"')

    def make_exception(self,msg):
        exc = BlockException(msg,self.context)
        return exc

    @abc.abstractmethod
    def to_action(self): return #pragma: no cover

    @abc.abstractmethod
    def expand_file_paths(self, root_dir): return #pragma: no cover
