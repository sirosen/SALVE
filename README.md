SALVE
=====

Authors: Stephen Rosen

Version: 1.0.2

For a detailed description of the project, please visit https://sirosen.github.io/SALVE

What can SALVE do?
==================

SALVE versions files and directories in a git repository, and handles the messy process of deploying those files onto a machine.
It is safer to use than shell scripts, and can be used to touch files, create directories, copy files and directories, apply permissions, and back up the preexisting versions of those files so that you can recover them if necessary at a later date.

To start writing manifests, browse the examples available at https://sirosen.github.io/SALVE/examples.html

For a more detailed description of the SALVE language, visit https://sirosen.github.io/SALVE/lang.html

Quick Start Guide
=================

The recommended way to use SALVE is to fork it and layer your own configuration on top of it.
By doing this, it becomes possible to pull in upstream changes from the stable branch of SALVE.

Deploy a ~/.bashrc
------------------
To get started by versioning your bashrc file, first fork the project on GitHub.
If your fork is "github.com:myuser/my-salve-fork.git", do the following
```
git clone git@github.com:myuser/my-salve-fork.git
cd my-salve-fork
cp ~/.bashrc bashrc
echo "file {
source bashrc
target $HOME/.bashrc
action copy
}" > bash.manifest
git add bashrc bash.manifest
git commit -m "Adding bashrc and simple manifest."
git push
```

then, to deploy your bashrc on another machine

```
git clone https://github.com/myuser/my-salve-fork
./my-salve-fork/salve.py --manifest my-salve-fork/bash.manifest
```

Changelog
=========
 * 1.0.2
    * Fewer actions rely on shell commands and use shutil instead
    * Underspecifying an action no longer causes a failure for chown and chmod, but skips these actions instead
    * File create now does a ```touch -a``` instead of a ```touch```, so that access time is changed instead of modified time
 * 1.0.1
    * Removed aggressive backups behavior that backed up directories and files on creation
    * Improved error reporting at levels of execution above the parser
 * 1.0.0
    * Addition of backups for overwritten files
    * Addition of SALVE_USER_PRIMARY_GROUP variable
    * Completed test coverage
 * beta 0.1.0
    * Addition of directory blocks
 * alpha 0.0.2
    * Added expansion of relative paths
    * Fixes for configuration templating in blocks
    * Checks EUID before attempting chown
 * alpha 0.0.1
    * Basic functionality for file blocks and manifest blocks
