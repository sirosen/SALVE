SALVE
=====

Author: Stephen Rosen

Version: 0.1.0

What is SALVE?
==============
SALVE is a language for deploying versioned configuration files.
An implementation of SALVE consists of a parser and execution package for Manifest files.
Manifests are lists of
 - Files with destinations, ugo permissions, owner, and group
 - Other manifests, excluding the current manifest's ancestors (i.e. no loops allowed)

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
The primary motivation is a confluence of two major factors:
  * Versioned configuration is good.
  * Configuration management systems are too complicated.

The issue is not whether or not Chef, Puppet, and Salt are good pieces of software, but they solve a different class of problem.
Existing configuration management software works around the notion of a configuration management server which polls and modifies nodes.
This complicates the core task of managing versioned configuration on an individual machine with logic and configuration relating to the interaction between the server and the managed nodes.
For a number of use cases -- a web developer who just wants to version control her personal webserver's configuration, or a programmer working in a VM who wants one .vimrc -- this is far beyond overkill.
SALVE aims to solve this problem in the simplest and most direct way possible.

The core philosophy is not disimilar to the common UNIX perspective on command line tools.
Rather than a few large, complicated tools that do everything, UNIX is built out of a large set of specialized tools that do their jobs well.
So too with SALVE, we have a tool that is not designed to fully satisfy every use case.
Instead, it is designed to solve a single problem well, and therefore to be possible to integrate with other tools.

Simplicity is Elegance
----------------------
One of the central design principles of this project is that an elegant system is a simple system.
The configuration language is extremely limited in its syntax, but does not encode very much of its semantics in the syntax.
Because the semantics are derived almost entirely from the choice of keywords, SALVE can be extended to support new uses almost trivially.

SALVE is Platform and Implementaiton Independent
================================================

Although Windows is not presently a target, the design is portable, and could be made to work with some, admittedly significant, effort.

SALVE is a Language, Not a Specific Implementation of that Language
-------------------------------------------------------------------
SALVE is a system for managing configuration, not an implementation of that system.
Although this version of the SALVE interpreter is written in python, it can equally well be described using Ruby, C, or even Pascal.
The only necessary components for an implementation of SALVE are
 - A manifest reader, which expands manifests into lists of actions
   - This is a tokenizer and parser, combined with an execution library that expands the resulting parse tree
 - A SALVE configuration loader
   - This can be an ini parser or just an environment variable inspector, though using the ini files is strongly recommended
   - The configuration is used to determine defaults, modify actions, and even tweak the interpreter itself
 - An execution module, which performs a list of actions in the order in which they are described in the manifests

SALVE Makes Few Assumptions
---------------------------
An implementation of SALVE should aim, as this one does, to have as few assumptions about the underlying OS as possible.
In theory, the same set of manifests should be runnable on any machine with a SALVE implementation in place.
In practice, restricting a set of manifests to run on Linux, Mac OSX, or other UNIX-like operating systems is a helpful simplifying assumption.
As of yet, the only universal assumption of which we are aware is that the underlying system is UNIX based.

SALVE Only Depends on What the Manifests Use
--------------------------------------------
SALVE does not rely on external tools like Debian's dpkg or OSX's MacPorts.
Ultimately, all that's required is a compiler or interpreter for the implementation, a working shell, and permissions to perform the operations requested in the Manifests.
At present, these actions are restricted to those that are predefined, as we do not yet support arbitrary shell commands.

SALVE Tries to Keep Your Safe
=============================
Although SALVE is, technically, an interpreted language, the parser, variable expansion, and safety checks prior to execution attempt to do thorough safety checking.
The ultimate goal is to ensure, as much as possible, that the requested actions can be executed successfully.
This includes validating acceptable values, and ensuring the effective UID grants sufficient permissions to perform actions.

Ultimately, the burden is on you to ensure that your configuration is correct, but SALVE will do its best to detect and abort on errors pertaining to botched specifications prior to any part of the execution beginning.

The SALVE Language
==================
What does a SALVE manifest actually look like?
Here we describe the basic format of a manifest file.

The Grammar
-----------

A manifest is a file containing expressions, _e,_ in the following basic grammar.
Some liberties have been taken with notation below.
```
e := Empty String
   | name { attrs } e

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

Variables
---------

SALVE supports the use of environment variables in templates.
These values will be pulled out of the executing shell's environment, and used to expand the attribute values of blocks in manifests.

There are a small number of exceptions to this.
```$SUDO_USER``` is inspected, and if set, used in place of ```$USER```.
At present, there is no way to specify the real value of ```$USER```, regardless of 'sudo' invocation, but this is in progress.
```$SALVE_ROOT``` always refers to the root directory of the SALVE repo.

Relative Paths
--------------

Relative paths are also supported, so that it is not necessary to rely on values like ```$SALVE_ROOT``` and ```$PWD```.
Relative paths are always interpreted relative to the root manifest's location.
One item on the docket is to make this an available override behavior via the fileroot commandline option, but to specify relative paths with respect to the dirname of the manifest that contains the block in question.

Example Manifest
----------------

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

Definitions
-----------

Each attribute of a block has a specific meaning, and many of the values themselves are keywords referring to specific actions.
Knowing these meanings is key to reading and understanding a manifest.
Below are the definitions of each manifest action, given in a subscript notation.
For example, ```file[action]``` specifies the 'action' attribute of 'file' blocks.

### file[action] ###
> 'file[action]=create' -- The create action copies 'file[source]' to 'file[target]'

### file[mode] ###
> 'file[mode]' -- This is the umask for UGO permissions on the created file

### file[user],file[group] ###
> 'file[user]' -- The owner of the created file
> 'file[group]' -- The owning group of the created file
Note that these attributes are ignored when salve is not run as root, since chowns cannot necessarily be applied.

### file[source], file[target] ###
> 'file[source]' -- The path to the file to be used, typically versioned in the configuration repo
> 'file[target]' -- The path to the file to which an action will be applied, or which will be created or destroyed


### manifest[source] ###
> 'manifest[source]' -- The path to the manifest to be expanded and executed at this location in the manifest tree


### directory[action] ###
> 'directory[action]=create' -- Create the directory at 'directory[target]', and any required ancestors
> 'directory[action]=copy' -- Create the directory at 'directory[target]', and then recursively copy contents from 'directory[source]' to 'directory[target]'

### directory[mode] ###
> 'directory[mode]' -- This is the umask for UGO permissions on the created directory

### directory[user],directory[group] ###
> 'directory[user]' -- The owner of the created directory
> 'directory[group]' -- The owning group of the created directory
Note that these attributes are ignored when salve is not run as root, since chowns cannot necessarily be applied.

### directory[source], directory[target] ###
> 'directory[source]' -- The path to the directory to be used, typically versioned in the configuration repo
> 'directory[target]' -- The path to the directory to which an action will be applied, or which will be created or destroyed

Sensible Defaults
-----------------

As much as possible, SALVE attempts to define all behavior on underspecified blocks.
These are our set of "sensible defaults", specified below in the format of a manifest.
A small class of values, when unspecified, result in errors or special behaviors.

```
file {
    mode    600
    user    $USER
    action  create
}

directory {
    mode    755
    user    $USER
    action  copy
}

manifest {
}
```

The special cases are
```
'file[group]' -- when unspecified, this is the primary group of the $USER
'directory[group]' -- when unspecified, this is the primary group of the $USER
```
