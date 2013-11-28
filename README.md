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

Notes
=====
 * At present, path specifications do not support ```~```, ```*```, or any other special characters for globbing, path expansion, and so forth.
 * The precedence order for values is naturally Specific Block > Block Defaults > Common Attributes, but this should be more clearly documented
 * Current variable expansion does not support vars which expand to other vars. This should be changed.
 * Screwing with the directory mode can create messy problems when writing to that dir. Recommend keeping mode umask for user as 7 for now.
 * When overwriting a file, SALVE needs read access in order to hash it and back it up.
