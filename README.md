SALVE
=====

Authors: Stephen Rosen

Version: 1.1.0

For a detailed description of the project, please visit http://sirosen.github.io/SALVE

What can SALVE do?
==================
SALVE versions files and directories in a git repository, and handles the messy process of deploying those files onto a machine.
It is safer to use than shell scripts, and backs up the preexisting versions of files that it changes so that you can recover them if necessary at a later date.

To start writing manifests, go to the Quick-Start guide at http://sirosen.github.io/SALVE/quickstart.html

For a more detailed description of the SALVE language, visit http://sirosen.github.io/SALVE/lang.html and browse the examples at http://sirosen.github.io/SALVE/examples.html

Roadmap
=======

These are the features and fixes currently in the pipeline for SALVE.
Generally Fixes are prioritized over Features, depending on their severity.

Features
--------
 - ```~``` and ```*``` expansion.
 - Git repository fetching
 - ```apt```, ```yum```, ```macports```, and ```homebrew``` support
    * Should ```pip``` and/or ```gem``` be added to the list?
 - Variable and attribute definition in manifest blocks to propogate down the block tree
 - Automagical backup recovery given a date
 - Addition of a mode that refuses to execute unless it can guarantee safety (and make this the default)
 - Track the expected state of the filesys to do more complete safety checking

Fixes
-----
 - Common attrs should be carried in an execution context, not expanded into block attrs
 - Dir alterations (chown/chmod) are based on walks at generation time, not execution time
 - Backups are stored by path/hash, which replicates any files that move but don't change
    * They should be stored by hash, and path mapping done in the logfile
    * This will break backwards log compatibility
 - Many backup/copy actions should check for checksum mismatches before performing an operation in order to reduce write load

Changelog
=========
 * 1.1.0
    * Large expansions to the testsuite
    * No SALVE actions are performed through the shell anymore
    * Permissions are now checked before actions are executed so that insufficient permissions will not crash the entire run
    * Error messages now take the common "[filename], line [lineno]: [message]" format
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
