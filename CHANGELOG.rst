Changelog
=========
 * 2.4.2
    * Fix a bug with setting the log level
    * Make the ``deploy`` subcommand the default when no subcommand is given
 * 2.4.1
    * SALVE now uses the python standard library for logging, rather than
      custom logging
    * Entire codebase (including tests) is now PEP8 and passes ``flake8``
    * Significant refactoring to improve Code Climate scoring
 * 2.4.0
    * Paths can be expanded relative to the manifest being processed, rather than
      relative to the root manifest (this will become the default in version 3)
 * 2.3.1
    * Fixes to setuptools usage
    * Change markdown documents to reST
 * 2.3.0
    * Support for Python 2.6 (with argparse installed)
    * Primary Attribute style blocks
    * Filesys abstraction layer
    * Removed ``SALVE_ROOT`` automatic variable
    * Relocated ``default_settings.ini`` to ``salve/default_settings.ini``
    * Default directory (without override) is directory of root manifest
 * 2.2.0
    * Travis and Coveralls integration
    * Improved internal logging and context handling
    * Support for Python 3
 * 2.1.0
    * Numerous log levels and output controls
    * Default attributes, which behave like the old 1.x version ``common`` attributes
    * Increased the context information produced when errors are raised
    * Regained code coverage in tests
    * Made the codebase PEP8 compliant (as per ``pep8`` v1.2)
 * 2.0.0
    * Backups are now stored in a flat dir by hash, resolving some dir/file conflict issues
    * Change to backup logfile timestamp format, more human readable
    * Old ``python salve.py`` usage is now ``python salve.py deploy``, and added stub ``python salve.py backup``
    * Switched to argparse -- now incompatible with python 2.6.x without libraries
    * ``common`` block attributes are now ``global``, and have precedence over block-defined attributes
    * Action verification checks and warnings on failures and skips
 * 1.1.0
    * Large expansions to the testsuite
    * No SALVE actions are performed through the shell anymore
    * Permissions are now checked before actions are executed so that insufficient permissions will not crash the entire run
    * Error messages now take the common ``[filename], line [lineno]: [message]`` format
 * 1.0.3
    * Fixes major bug with dir copy not triggering file backups
    * Internal refactoring and cleanup in Blocks and Actions
 * 1.0.2
    * Fewer actions rely on shell commands and use ``shutil`` instead
    * Underspecifying an action no longer causes a failure for chown and chmod, but skips these actions instead
    * File create now does a ``touch -a`` instead of a ``touch``, so that access time is changed instead of modified time
 * 1.0.1
    * Removed aggressive backups behavior that backed up directories and files on creation
    * Improved error reporting at levels of execution above the parser
 * 1.0.0
    * Addition of backups for overwritten files
    * Addition of ``SALVE_USER_PRIMARY_GROUP`` variable
    * Completed test coverage
 * beta 0.1.0
    * Addition of directory blocks
 * alpha 0.0.2
    * Expansion of relative paths
    * Fixes for configuration templating in blocks
    * Checks EUID before attempting chown
 * alpha 0.0.1
    * Basic functionality for file blocks and manifest blocks
