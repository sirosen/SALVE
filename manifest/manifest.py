#!/usr/bin/python

from __future__ import print_function
import os

import line

class Manifest(object):
    def __init__(self, filename, ancestors=None, root=None, dirname=None):
        """
        @filename is the name of a manifest file which contains valid
        directives, including submanifests.

        @ancestors are the manifest filenames that have already
        been encountered in the course of recursive submanifest
        expansion. They are ancestors of the current manifest, tracked
        so that SALVE can ensure that no manifest includes itself.

        @root is the root of the ancestor tree and used to specify
        that a submanifest should not build an independent list of
        lines, but simply append to the root.

        A manifest is really just a list of of Lines, in the order
        that they are meant to be done.
        """
        # ancestors must exist
        if not ancestors: ancestors = set()

        if filename in ancestors:
            raise LookupError('%s is a manifest that includes itself!' % filename)
        else:
            ancestors.add(filename)

        # when there is no root, set it to be a self-pointer
        if not root: root = self

        # when the directory is not specified, it is assumed
        # to be the one containing the manifest
        if not dirname: dirname = os.path.dirname(filename)

        self.filename = filename
        self.lines = []
        with open(filename) as f:
            for rawline in f:
                parsed = line.parse_line(rawline, dirname)
                if isinstance(parsed, line.EmptyLine):
                    pass
                elif isinstance(parsed, line.ManifestLine):
                    # an explcit create and delete with root
                    # appends the manifests lines to the root
                    man = Manifest(parsed.filename, ancestors, root, dirname)
                    del man
                else:
                    root.append(parsed)

        ancestors.remove(filename)

    def append(self, line_obj):
        self.lines.append(line_obj)
