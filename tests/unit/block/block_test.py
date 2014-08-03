#!/usr/bin/python

from nose.tools import istest
from tests.utils.exceptions import ensure_except

from salve.block import Block
from salve.util.context import FileContext


@istest
def block_is_abstract():
    """
    Unit: Block Base Class Is Abstract
    Ensures that a Block cannot be instantiated.
    """
    ensure_except(TypeError, Block, Block.types.FILE,
            FileContext('no such file'))
