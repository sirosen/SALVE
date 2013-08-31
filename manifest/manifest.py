#!/usr/bin/python

from __future__ import print_function
import os

import line, action

class Manifest(object):
    def __init__(self, filename, ancestors=None, dirname=None):
        """
        @filename is the name of a manifest file which contains valid
        directives, including submanifests.

        @ancestors are the manifest filenames that have already
        been encountered in the course of recursive submanifest
        expansion. They are ancestors of the current manifest, tracked
        so that SALVE can ensure that no manifest includes itself.

        A manifest is really just a list of of Actions, in the order
        that they are meant to be done.
        """
        # ancestors must exist
        if not ancestors: ancestors = set()

        # forbid circular manifests
        if filename in ancestors:
            raise LookupError('%s is a manifest that includes itself!' % filename)
        else:
            ancestors.add(filename)

        # when the directory is not specified, it is assumed
        # to be the one containing the manifest
        if not dirname: dirname = os.path.dirname(filename)

        self.filename = filename
        # the actionlist starts empty
        self.actions = action.ActionList([])
        with open(filename) as f:
            for rawline in f:
                parsed = line.parse_line(rawline, dirname)
                if isinstance(parsed, line.EmptyLine):
                    pass
                elif isinstance(parsed, line.ManifestLine):
                    # create the submanifest (ensures ancestor safety)
                    # but delete it once we have its actions
                    man = Manifest(parsed.filename, ancestors, root, dirname)
                    self.append(man.actions)
                    del man
                else:
                    self.append(Action(parsed))

        ancestors.remove(filename)

    def append(self, act):
        self.actions.append(act)
