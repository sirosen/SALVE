.. image:: https://travis-ci.org/sirosen/SALVE.svg?branch=dev
    :alt: Build Status
    :target: https://travis-ci.org/sirosen/SALVE
.. image:: https://coveralls.io/repos/sirosen/SALVE/badge.png?branch=dev
    :alt: Coverage Status
    :target: https://coveralls.io/r/sirosen/SALVE?branch=dev
.. image:: https://badge.fury.io/py/salve.svg
    :alt: PyPi Version
    :target: https://badge.fury.io/py/salve
.. image:: https://codeclimate.com/github/sirosen/SALVE/badges/gpa.svg
   :target: https://codeclimate.com/github/sirosen/SALVE
   :alt: Code Climate

SALVE
=====

SALVE takes files and directories in a git repository, and handles the messy
process of deploying those files onto a machine.
It is safer to use than shell scripts in a number of ways, and guarantees
idempotence -- an oft-sought property for configuration management tools -- for
a wide class of deployment actions.
It also backs up the preexisting versions of files that it changes when
possible so that you can recover them if necessary at a later date.

More information is available at `SALVE Website <http://salve.sirosen.net/>`_.

How do I use it?
================

SALVE is a language, but also a compiler for that language written in python.
You write "manifests" which describe where your files are meant to go, and
SALVE validates that you can put them where you want before doing anything at
all.
It means learning a new language, but it also lets you specify how your config
should be deployed in a more natural way, and protects you from a wide range of
dangerous errors.
The language is small and simple enough that you can learn all of the important
parts in a few minutes, and answer any remaining questions in under half an
hour.

To start writing manifests, you can go to the `Quick-Start Guide <http://salve.sirosen.net/quickstart.html>`_.
For a more detailed description of the SALVE language, the `Language Page <http://salve.sirosen.net/lang>`_ and the `Examples Page <http://salve.sirosen.net/lang/examples.html>`_ are good resources.

Once you have a manifest you want to run, simply do a ``salve deploy`` with them.
If you have installed the pip package, you can run

    salve deploy --manifest path/to/root.manifest

or, if you are using the git repo as your source

    python SALVE/salve.py deploy --manifest path/to/root.manifest

What do I need to run it?
=========================

SALVE is fully compatible with Python 2.6, 2.7, 3.2, 3.3, 3.4, and 3.5.
It also works on pypy and pypy3.

It has no dependencies on python packages, so as long as you have one of these
versions of Python installed, you can run SALVE.
That means that you can always pull down the git repo and run it even on
machines that don't have ``pip`` or ``easy_install``.

Python 2.6 Support
------------------

Python 2.6 is supported, but because OptParse is deprecated in Python 3.x,
SALVE depends upon ``argparse``.

To run SALVE with Python 2.6, you will need to install the ``argparse``
package, or do a ``pip`` or ``easy_install`` of ``salve`` to pull in the
dependency automatically.

Roadmap
=======

The Roadmap has been replaced with
`GitHub issues <https://github.com/sirosen/SALVE/issues>`_.
