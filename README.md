SALVE
=====

Author: Stephen Rosen

Version: 0.0.1

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

Simple, because SALVE aims to be 100% understandable.
Any manifest can be reasoned about as a sequential execution of commands.

Local, because SALVE does not involve a centralized configuration server.

Versioning, because SALVE is designed to operate on version controlled configuration.

Ecosystem, because SALVE is designed to manage configuration for any purpose on your system, ranging from personalized config files (bashrc, emacs config), to system wide properties (nginx site files, init scripts).

Why SALVE?
==========
SALVE is designed to make your life easier, not harder, your configuration simpler, not more complicated, and to let you do it YOUR way, no matter how right or wrong your way might be.
The motivation for SALVE is a confluence of two major factors:
  * Versioned configuration is good.
  * Configuration management systems are too complicated.

The issue is not whether or not Chef, Puppet, and Salt are good pieces of software, but they solve a different class of problem from SALVE.
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
One of the core design principles of this project is that an elegant system is a simple system.
The configuration language is extremely limited in its syntax, but does not encode very much of its semantics in the syntax.
Because the semantics are derived almost entirely from the choice of keywords, SALVE can be extended to support new uses almost trivially.

SALVE is Platform and Language Independent
==========================================

Although Windows is not presently a target for SALVE, the design is portable, and could be made to work with some, admittedly significant, effort.

SALVE is Not Implemented in a Language
--------------------------------------
SALVE is a system for managing configuration, not an implementation of that system.
Although this version of the system consists of python, it can equally well be described using Ruby, C, or even Pascal.
The only necessary components for an implementation of SALVE are
 - A manifest parser, which expands manifests into lists of actions
 - A SALVE configuration loader
   - This can be an ini parser or just an environment variable inspector, though using the ini files is strongly recommended
   - The configuration must be used to determine the behavior of the defined actions
 - An execution module, which performs a list of actions in the order in which they are listed

SALVE Makes Few Assumptions
---------------------------
An implementation of SALVE should aim, as this one does, to have as few assumptions about the underlying OS as possible.
In theory, the same set of manifests should be runnable on any machine with a SALVE implementation in place.
In practice, restricting a set of manifests to run on Linux, Mac OSX, or other UNIX-like operating systems is a helpful simplifying assumption.
As of yet, the only universal assumption of which we are aware is that the underlying system is UNIX based.

SALVE Only Depends on What the Manifests Use
--------------------------------------------
SALVE does not rely on external tools like Debian's dpkg or OSX's MacPorts.
Ultimately, all that's required is a compiler or interpreter for the SALVE implementation, a working shell, and permissions to perform the operations requested in the Manifests.
At present, these actions are restricted to those that are predefined, as SALVE does not yet support arbitrary shell commands.
