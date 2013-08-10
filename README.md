What is SALVE?
==============
SALVE: A Cure For All Hurts is an architecture for deploying versioned configuration files locally.
An implementation of SALVE consists of a parser and execution package for Manifest files.
Manifests are lists of
 - Files with destinations, ugo permissions, owner, and group
 - Shell commands to execute before, after, and while deploying files, including script invocations
 - Other manifests, so that we can have manifests all the way down! (do not attempt in 3-space)

Why SALVE?
==========
SALVE is designed to make your life easier, not harder, your configuration simpler, not more complicated, and to let you do it YOUR way, no matter how right or wrong your way might be.
The motivation for SALVE is a confluence of two major factors:
1) Versioned configuration is good.
2) Configuration management systems are too complicated.

The issue is not whether or not Chef, Puppet, and Salt are good pieces of software, but they solve a different class of problem from SALVE.
Existing configuration management software works around the notion of a configuration management server which polls and modifies nodes.
This complicates the core task of managing versioned configuration on an individual machine with logic and configuration relating to the interaction between the server and the managed nodes.
For a number of use cases -- a web developer who just wants to version control her personal webserver's configuration, or a programmer working in a VM who wants one .vimrc -- this is far beyond overkill.
SALVE aims to solve this problem in the simplest, most direct, and most robust way possible.

Simplicity is Elegance
----------------------
One of the core design principles of this project is that an elegant system is a simple system.
In its architecture, even Chef is exceedingly simple: a single server holds configuration and pushes it out to the target nodes, and developers push configuration up to the server.
SALVE, however, is the extremity of KISS.
The end result is versioned-configuration-in-a-box.

SALVE is Platform and Language Independent
==========================================

Although Windows is not presently a target for SALVE, the design is portable, and could be made to work with some, admittedly significant, effort.

SALVE is Not Written in a Language
----------------------------------
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
As of yet, the only assumption of which we are aware is that the underlying system is UNIX based.

SALVE Only Depends on What the Manifests Use
--------------------------------------------
SALVE does not rely on external tools like Debian's dpkg or OSX's MacPorts.
Ultimately, all that's required is a compiler or interpreter for the SALVE implementation, a working shell, and permissions to perform the operations requested in the Manifests.
