#!/usr/bin/python

from nose.tools import istest, with_setup
import mock, StringIO, os, subprocess

import src.run.command

scratch_dir = os.path.join(os.path.dirname(__file__),'scratch')

def run_on_args(argv):
    with mock.patch('sys.argv',argv):
        return src.run.command.main()

def make_scratch():
    p = subprocess.Popen('mkdir -p %s' % scratch_dir,
                         shell=True)
    p.wait()
    assert p.returncode == 0

def rm_scratch():
    p = subprocess.Popen('rm -r %s' % scratch_dir,
                         shell=True)
    p.wait()
    assert p.returncode == 0

def write_scratchfile(relpath,content):
    with open(os.path.join(scratch_dir,relpath),'w') as f:
        f.write(content)

def read_scratchfile(relpath):
    with open(os.path.join(scratch_dir,relpath),'r') as f:
        return f.read()

@istest
@with_setup(make_scratch,rm_scratch)
def copy_single_file():
    """
    E2E: Copy a Single File

    Runs a manifest which copies itself and verifies the contents of
    the destination file.
    """
    cwd = scratch_dir
    content = 'file { action copy source 1.man target 2.man }\n'
    write_scratchfile('1.man',content)
    man_path = os.path.join(cwd,'1.man')
    run_on_args(['./salve.py','-m',man_path])
    s = read_scratchfile('2.man')
    assert s == content, '%s' % s

@istest
@with_setup(make_scratch,rm_scratch)
def copy_two_files():
    """
    E2E: Copy Two Files

    Runs a manifest which copies two files and verifies the contents of
    the destination files.
    """
    cwd = scratch_dir
    man_path = os.path.join(cwd,'1.man')
    write_scratchfile('1.man',
        'file { action copy source f1 target f1prime }\n'+\
        'file { source f2 target f2prime }\n'
        )
    f1_content = 'alpha beta\n'
    f2_content = 'gamma\ndelta\n'
    write_scratchfile('f1',f1_content)
    write_scratchfile('f2',f2_content)

    run_on_args(['./salve.py','-m',man_path])
    s = read_scratchfile('f1prime')
    assert s == f1_content, '%s' % s
    s = read_scratchfile('f2prime')
    assert s == f2_content, '%s' % s
