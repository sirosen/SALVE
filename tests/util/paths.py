from salve import paths


testfile_dir = paths.pjoin(
    paths.containing_dir(__file__, depth=2),
    'testfiles')


def full_path(filename):
    return paths.pjoin(testfile_dir, filename)
