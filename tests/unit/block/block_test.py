#!/usr/bin/python

from nose.tools import istest
from tests.utils.exceptions import ensure_except

import salve.block.base


@istest
def block_is_abstract():
    """
    Block Base Class Is Abstract
    Ensures that a Block cannot be instantiated.
    """
    ensure_except(TypeError, salve.block.base.Block)
