SALVE
=====

Authors: Stephen Rosen

Version: 1.0.3

For a detailed description of the project, please visit http://sirosen.github.io/SALVE

What can SALVE do?
==================

SALVE versions files and directories in a git repository, and handles the messy process of deploying those files onto a machine.
It is safer to use than shell scripts, and can be used to touch files, create directories, copy files and directories, apply permissions, and back up the preexisting versions of those files so that you can recover them if necessary at a later date.

To start writing manifests, go to the Quick-Start guide at http://sirosen.github.io/SALVE/quickstart.html

For a more detailed description of the SALVE language, visit http://sirosen.github.io/SALVE/lang.html and browse the examples at http://sirosen.github.io/SALVE/examples.html

Changelog
=========
 * 1.0.3
    * Fixes major bug with dir copy not triggering file backups
    * Internal refactoring and cleanup in Blocks and Actions
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
