from nose.tools import eq_

from salve.filesys import ConcreteFilesys


def verification_produces_code(act, code_name, filesys=None):
    if not filesys:
        filesys = ConcreteFilesys()

    code = act.verification_codes[code_name]
    produced_code = act.verify_can_exec(filesys)

    eq_(produced_code, code)
