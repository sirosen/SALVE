#!/usr/bin/python

import abc

from src.util.enum import Enum

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

    def set(self,attribute_name,value):
        self.attrs[attribute_name] = value

    def get(self,attribute_name):
        return self.attrs[attribute_name]

    def ensure_has_attrs(self,*args):
        for attr in args:
            if attr not in self.attrs:
                raise BlockException('Block(ty='+self.block_type+') '+\
                                     'missing attr "'+attr+'"')

    @abc.abstractmethod
    def to_action(self): return

    @abc.abstractmethod
    def expand_file_paths(self, root_dir): return
