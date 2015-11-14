.. image:: https://travis-ci.org/sirosen/SALVE.svg?branch=stable
    :alt: Build Status
    :target: https://travis-ci.org/sirosen/SALVE
.. image:: https://coveralls.io/repos/sirosen/SALVE/badge.png?branch=stable
    :alt: Coverage Status
    :target: https://coveralls.io/r/sirosen/SALVE?branch=stable
.. image:: https://badge.fury.io/py/salve.svg
    :alt: PyPi Version
    :target: https://badge.fury.io/py/salve
.. image:: https://codeclimate.com/github/sirosen/SALVE/badges/gpa.svg
   :alt: Code Climate
   :target: https://codeclimate.com/github/sirosen/SALVE

SALVE
=====

SALVE takes files and directories in a git repository, and handles the messy
process of deploying those files onto a machine.

More information is available at the `SALVE Website <http://salve.sirosen.net/>`_.

How do I use it?
================

SALVE is a language, but also a compiler and runtime for that language.
You write "manifests" which describe where your files are meant to go, and
SALVE will do the rest.
The language is small and simple enough that you can learn all of the important
parts in a few minutes, and answer any remaining questions in under half an
hour.

To start writing manifests, you can go to the `Quick-Start Guide <http://salve.sirosen.net/quickstart.html>`_.
For a more detailed description of the SALVE language, the `Language Page <http://salve.sirosen.net/lang>`_ and the `Examples Page <http://salve.sirosen.net/lang/examples.html>`_ are good resources.

Once you have a manifest you want to run, simply do ``salve deploy`` with it.
If you have installed the pip package, you can run

    salve deploy --manifest path/to/root.manifest

or, if you are using the git repo as your source

    python SALVE/salve.py deploy --manifest path/to/root.manifest

Since ``deploy`` is the default action, you could also run

    salve -m path/to/root.manifest

What do I need to run it?
=========================

SALVE is fully compatible with Python 2.6, 2.7, 3.2, 3.3, 3.4, and 3.5.
It also works on pypy and pypy3.

It has no dependencies on other python packages, so as long as you have one of
these versions of Python installed, you can run SALVE.

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
