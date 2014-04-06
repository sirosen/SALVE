SALVE
=====

Authors: Stephen Rosen

Version: 2.1.0

For a detailed description of the project, please visit the [SALVE Official Site](http://salve.sirosen.net/ "SALVE")

What can SALVE do?
==================
SALVE versions files and directories in a git repository, and handles the messy process of deploying those files onto a machine.
It is safer to use than shell scripts in a few ways, and guarantees idempotence for a wide class of deployment actions.
It also backs up the preexisting versions of files that it changes when possible so that you can recover them if necessary at a later date.

To start writing manifests, you can go to the [Quick-Start Guide](http://salve.sirosen.net/quickstart.html "SALVE Quick-Start").
For a more detailed description of the SALVE language, [the SALVE Language Page](http://salve.sirosen.net/lang.html "SALVE Language") and [the Examples Page](http://salve.sirosen.net/examples.html "SALVE Examples") are good resources.

Roadmap
=======

These are the features and fixes currently in the pipeline for SALVE.
Generally Fixes are prioritized over Features, depending on their severity.

Features
--------
 - Plugin framework
 - Variable and attribute definition in manifest blocks to propogate down the block tree as defaults
 - Automatic file backup recovery using dates, generation numbers, and so forth

Fixes
-----
 - ```~``` and ```*``` expansion does not offer useful error messages.
 - Verification is performed on a rolling basis, rather than once at the start of execution
 - Dir alterations (chown/chmod) are based on walks at generation time, not execution time

Changelog
=========
 * 2.1.0
    * Added numerous log levels and output controls
    * Added default attributes, which behave like the old "common" attributes
    * Increased the context information produced when errors are raised
 * 2.0.0
    * Backups are now stored in a flat dir by hash, resolving some dir/file conflict issues
    * Change to backup logfile timestamp format, more human readable
    * Old ```python salve.py``` usage is now ```python salve.py deploy```, and added stub ```python salve.py backup```
    * Switched to argparse -- now incompatible with python 2.6.x without libraries
    * 'common' block attributes are now 'global', and have precedence over block-defined attributes
    * Action verification checks and warnings on failures and skips
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
