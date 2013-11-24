SALVE
=====

Authors: Stephen Rosen

Version: 1.0.0

What is SALVE?
==============
SALVE is a language for deploying configuration files.
It's purpose is to make it simple to keep configuration versioned in a VCS, then deploy it in a UNIX filesystem.

A SALVE repository holds the full source for SALVE, any configuration files, and a set of Manifest files.
Manifests are lists of
 * Files and directories with destinations, ugo permissions, owner, and group
 * Other manifests, excluding the current manifest and its ancestors (i.e. no loops allowed)

Typically, a SALVE repository also holds one root manifest, which lists all of the other manifests to be used.

What Does "SALVE" Stand For?
============================
SALVE is the Simple And Local Versioning Ecosystem.

Simple, because it aims to be 100% understandable.
Any manifest can be reasoned about as a sequential execution of commands.

Local, because it does not involve a centralized configuration server.

Versioning, because it is designed to operate on version controlled configuration.

Ecosystem, because it is designed to manage configuration for any purpose on your system, ranging from personalized config files (bashrc, emacs config), to system wide properties (nginx site files, init scripts).

Why SALVE?
==========
SALVE is designed to make your life easier, not harder, your configuration simpler, not more complicated, and to let you do it YOUR way, no matter how right or wrong your way might be.
The primary motivation is a confluence of two major factors: versioned configuration is good and configuration management systems are too complicated.

The Server-Node Architecture is Sometimes Overcomplicated
---------------------------------------------------------
Most configuration management software works around the notion of a configuration management server which polls and modifies nodes.
This complicates the core task of managing configuration on an individual machine with logic relating to the interaction between the server and the managed nodes.

Furthermore, with Puppet, Chef, and similar tools, the capacity for node introspection makes knowing what will hppen on deployment very hard.
Machines can ask questions "Am I listed as a 'web-server'? Am I in the 'nagios-monitored' group?" and dispatch on the answers.

With SALVE, you instead keep a version controlled directory of configuration, and manage it as you see fit.
It is recommended to do this using one of the large free git server providers like GitHub.
When you want to deploy on a node, all you need to do to know how a deployment will run is ensure that the local repository is up-to-date.
This dramatically simplified approach is much more suitable to personal configuration, and may even be appropriate for some small-scale Ops.

Goal-Oriented Systems are Hard to Understand
--------------------------------------------
Furthermore, almost all of the server-node based systems are "goal oriented".
Rather than listing a set of commands, they try to describe the desired state of the system, and then put it in that state.
This makes it hard to understand the flow of execution, especially in the presence of errors.

By contrast, SALVE execution is purely sequential, meaning that it should be possible to read manifests top to bottom and know what will be executed.
This should hold regardless of the machine state.

One of the main advantages of goal-oriented configuration is that it guarantees that multiple runs are idempotent.
SALVE aims to solve this problem in the simplest and most direct way possible, by using a DSL which only supports descriptions of idempotent actions.

Simplicity is Elegance
----------------------
The core philosophy is not disimilar to the common UNIX perspective on command line tools.
Rather than a few large, complicated tools that do everything, UNIX is built out of a large set of specialized tools that do their jobs well.
So too with SALVE, we have a tool that is not designed to fully satisfy every use case.
Instead, it is designed to solve a single problem well, and therefore to be possible to integrate with other tools.

One of the central design principles of this project is that an elegant system is a simple system.
The configuration language is extremely limited in its syntax, but does not encode very much of its semantics in the grammar.
Because the semantics are derived almost entirely from the choice of keywords, SALVE can be extended to support new uses almost trivially.

Minimal Dependencies and Assumptions
====================================

Although Windows is not presently a target, the design is portable, and could be made to work with some, admittedly significant, effort.

SALVE Only Depends on What the Manifests Use
--------------------------------------------
SALVE does not rely on external tools like Debian's dpkg or OSX's MacPorts.
Ultimately, all that's required is python2.7+, a working shell, and permissions to perform the operations requested in the Manifests.
At present, these actions are restricted to those that are predefined, as we do not yet support arbitrary shell commands.

SALVE does not use any python eggs or other packages, and attempts to depend more on python's extensive set of builtins than shell commands.
For example, hashing is done with python's hashlib, rather than sha512sum, md5sum, and so forth.

SALVE Tries to Keep Your Safe
-----------------------------
SALVE does not assume that you can actually perform all of the actions you requested.
The system may have broken permissions for some directories, or you may have made mistakes in your specification of manifests.
Although SALVE is, technically, an interpreted language, the parser, variable expansion, and safety checks prior to execution attempt to be thorough in preventing calamities.

The ultimate goal is to ensure, as much as possible, that the requested actions can be executed successfully.
This includes validating acceptable values, and ensuring the effective UID grants sufficient permissions to perform actions.
Ultimately, the burden is on you to ensure that your configuration is correct, but SALVE will do its best to detect and abort on errors pertaining to botched specifications prior to any part of the execution beginning.

The SALVE Language
==================
What does a SALVE manifest actually look like?
Here we describe the basic format of a manifest file.

Example Manifest
----------------
We begin with an example, which will be broken down and explained in the sections below.

```
file {
    source  files/bash/bashrc
    target  $HOME/.bashrc
    mode    600
}

directory {
    source  dirs/dircolors
    target  $HOME/dircolors
    action  copy
}

file {
    source  /etc/passwd
    target  /opt/myprog/passwd-clone
    mode    0440
    user    admin
    group   root
}

manifest {
    source  manifests/vim.manifest
}
```


The Grammar
-----------

A manifest is a file containing expressions, _e,_ in the following basic grammar.
Some liberties have been taken with notation below.
```
e := Empty String
   | block_id { attrs } e

block_id := "file"
          | "directory"
          | "manifest"

attrs := Empty String
       | name value attrs

name := namechar name
      | namechar

namechar := alpha
          | digit
          | "_"

value := valuechar value
       | valuechar
       | '"' quotedvalue '"'
       | "'" quotedvalue "'"

quotedvalue := quotedchar quotedvalue
             | quotedchar

quotedchar := valuechar | " "

valuechar := namechar
           | "_" | "-" | "+"
           | "=" | "^" | "&"
           | "@" | "`" | "/"
           | "|" | "~" | "$"
           | "(" | ")" | "["
           | "]" | "." | ","
           | "<" | ">" | "*"
           | "?" | "!" | "%"
           | "#"
```

Note that this only defines the grammar of acceptable SALVE expressions
for the parser.
There are further constraints upon what keywords are valid and carry
meaning.
Those are defined below.

Variables
---------

SALVE supports the use of environment variables in templates.
These values will be pulled out of the executing shell's environment, and used to expand the attribute values of blocks in manifests.

There are a small number of exceptions to this.

```SUDO_USER``` is inspected, and if set, used in place of ```USER```.
At present, there is no way to specify the real value of ```USER```, regardless of 'sudo' invocation, but this is in progress.

```SALVE_ROOT``` always refers to the root directory of the SALVE repo.

```SALVE_USER_PRIMARY_GROUP``` always refers to the primary group of ```USER```, after ```SUDO_USER``` substitution.

```HOME``` always refers to the home directory of ```USER``` after ```SUDO_USER``` substitution.
This ensures that ```HOME``` always refers to the invoking user's homedir, even if sudo is set to reset the ```HOME``` environment variable.

### Example ###
Given the block below
```
file {
    source  files/bash/bashrc
    target  $HOME/.bashrc
    mode    600
}
```
When SALVE is invoked by a user, "user1", with home directory "/home/user1",
the value of "target" after expansion is "/home/user1/.bashrc"
This holds even when "user1" invokes SALVE with sudo.

Relative Paths
--------------

Relative paths are also supported, so that it is not necessary to rely on values like ```$SALVE_ROOT``` and ```$PWD```.
Relative paths are always interpreted relative to the root manifest's location.
One item on the docket is to make this an available override behavior via the fileroot commandline option, but to specify relative paths with respect to the dirname of the manifest that contains the block in question.

### Example ###
Given the block below
```
file {
    source  files/bash/bashrc
    target  $HOME/.bashrc
    mode    600
}
```
if SALVE is invoked as ```python salve.py -m /tmp/myconf/root.manifest```,
then the value of "source" after expansion is "/tmp/myconf/files/bash/bashrc"

Definitions
-----------

Each attribute of a block has a specific meaning, and many of the values themselves are keywords referring to specific actions.
Knowing these meanings is key to reading and understanding a manifest.
Below are the definitions of each manifest action, given in a subscript notation.
For example, ```file[action]``` specifies the 'action' attribute of 'file' blocks.

### file[action] ###

> 'file[action]=copy' -- The copy action copies 'file[source]' to 'file[target]'

> 'file[action]=create' -- The create action touches 'file[target]'

### file[mode] ###

> 'file[mode]' -- This is the umask for UGO permissions on the created file

### file[user], file[group] ###

> 'file[user]' -- The owner of the created file

> 'file[group]' -- The owning group of the created file
Note that these attributes are ignored when salve is not run as root, since chowns cannot necessarily be applied.

### file[source], file[target] ###

> 'file[source]' -- The path to the file to be used, typically versioned in the configuration repo

> 'file[target]' -- The path to the file to which an action will be applied, or which will be created or destroyed

### file[backup\_dir], file[backup\_log] ###

> 'file[backup\_dir]' -- The path to the directory in which file backups are stored

> 'file[backup\_log]' -- The path to the file to which backup actions are logged (date, hash, full path to file)


### manifest[source] ###

> 'manifest[source]' -- The path to the manifest to be expanded and executed at this location in the manifest tree


### directory[action] ###

> 'directory[action]=create' -- Create the directory at 'directory[target]', and any required ancestors

> 'directory[action]=copy' -- Create the directory at 'directory[target]', and then recursively copy contents from 'directory[source]' to 'directory[target]'

### directory[mode] ###

> 'directory[mode]' -- This is the umask for UGO permissions on the created directory

### directory[user], directory[group] ###

> 'directory[user]' -- The owner of the created directory

> 'directory[group]' -- The owning group of the created directory
Note that these attributes are ignored when salve is not run as root, since chowns cannot necessarily be applied.

### directory[source], directory[target] ###

> 'directory[source]' -- The path to the directory to be used, typically versioned in the configuration repo

> 'directory[target]' -- The path to the directory to which an action will be applied, or which will be created or destroyed

### directory[backup\_dir], directory[backup\_log] ###

> 'directory[backup\_dir]' -- The path to the directory in which file backups are stored

> 'directory[backup\_log]' -- The path to the file to which backup actions are logged (date, hash, full path to file)


Sensible Defaults
-----------------

As much as possible, SALVE attempts to define all behavior on underspecified blocks.
These are our set of "sensible defaults", specified below in the format of a manifest.
A small class of values, when unspecified, result in errors.
These are generally the variables that refer to paths.

There is a special set of attributes, specified as "common" in the default settings, which describe values shared by all blocks unless explicitly overridden.


```
common {
    backup_dir  $HOME/.salve/backups
    backup_log  $HOME/.salve/backup.log
    backup_log
}

file {
    mode    600
    user    $USER
    group   $SALVE_USER_PRIMARY_GROUP
    action  copy
}

directory {
    mode    755
    user    $USER
    group   $SALVE_USER_PRIMARY_GROUP
    action  copy
}

manifest {
}
```

Notes
=====
 * At present, path specifications do not support ```~```, ```*```, or any other special characters for globbing, path expansion, and so forth.
 * The precedence order for values is naturally Specific Block > Block Defaults > Common Attributes, but this should be more clearly documented
 * Current variable expansion does not support vars which expand to other vars. This should be changed.
 * Screwing with the directory mode can create messy problems when writing to that dir. Recommend keeping mode umask for user as 7 for now.
 * When overwriting a file, SALVE needs read access in order to hash it and back it up.

My Thanks for Design Input From
-------------------------------
 * Bryce Allen
 * Jeremy Archer
 * Bryce Lanham
 * Minke Zhang
