SALVE
=====

Authors: Stephen Rosen

Version: 1.0.1

For a detailed description of the project, please visit https://sirosen.github.io/SALVE

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

What can SALVE do?
------------------

SALVE versions files and directories in a git repository, and handles the messy process of deploying those files onto a machine.
It can touch files, create directories, copy files and directories, and back up the preexisting versions of those files so that you can recover them if necessary at a later date.
It can also apply permissions, owner, and group, and expands variables in the calling shell's environment.

Importantly, SALVE deployments are idempotent, so multiple runs of SALVE have no effect on your system, and upgrading a file from one version to another merely consists of updating the SALVE repo, pulling, and rerunning the tool.

It gives best effort protection against disallowed actions, and guarantees the validity of a manifest or manifest tree before execution.
This makes it much safer and more reliable to deploy configuration with SALVE than shell scripts.

To start writing manifests, read the grammar below, or browse the examples in the SALVE examples directory.
For a more detailed description of the SALVE language, visit https://sirosen.github.io/SALVE/lang.html

The SALVE Language Basics
=========================

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

Relative Paths
--------------

Relative paths are also supported, so that it is not necessary to rely on values like ```$SALVE_ROOT``` and ```$PWD```.
Relative paths are always interpreted relative to the root manifest's location.

Definitions
-----------

Below are the definitions of each manifest block attribute, given in a subscript notation.

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

Notes
=====
 * At present, path specifications do not support ```~```, ```*```, or any other special characters for globbing, path expansion, and so forth.
 * The precedence order for values is naturally Specific Block > Block Defaults > Common Attributes, but this should be more clearly documented
 * Current variable expansion does not support vars which expand to other vars. This should be changed.
 * Screwing with the directory mode can create messy problems when writing to that dir. Recommend keeping mode umask for user as 7 for now.
 * When overwriting a file, SALVE needs read access in order to hash it and back it up.
