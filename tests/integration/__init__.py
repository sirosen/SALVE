#!/usr/bin/python

from salve.util import locations

_testfile_dir = locations.pjoin(
        locations.containing_dir(__file__, depth=2),
        'testfiles')


def get_full_path(filename):
    return locations.clean_path(locations.pjoin(_testfile_dir, filename))
