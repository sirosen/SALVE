.. image:: https://travis-ci.org/sirosen/SALVE.svg?branch=stable
    :alt: Build Status
    :target: https://travis-ci.org/sirosen/SALVE
.. image:: https://coveralls.io/repos/sirosen/SALVE/badge.png?branch=stable
    :alt: Coverage Status
    :target: https://coveralls.io/r/sirosen/SALVE?branch=stable

.. image:: https://codeclimate.com/github/sirosen/SALVE/badges/gpa.svg
   :alt: Code Climate
   :target: https://codeclimate.com/github/sirosen/SALVE
.. image:: https://api.codacy.com/project/badge/grade/83b4ee7bcc41437a8172e0f23af5db5e
   :alt: Codacy
   :target: https://www.codacy.com/app/sirosen/SALVE

.. image:: https://badge.fury.io/py/salve.svg
    :alt: PyPi Version
    :target: https://badge.fury.io/py/salve
.. image:: https://img.shields.io/pypi/pyversions/salve.svg
    :alt: Supported Pythons
    :target: https://img.shields.io/pypi/pyversions/salve.svg
.. image:: https://img.shields.io/pypi/implementation/salve.svg
    :alt: Supported Python Implementations
    :target: https://img.shields.io/pypi/implementation/salve.svg

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

No Dependencies, Except Python 2.6
==================================

SALVE has no dependencies on other python packages, so as long as you have a
supported Python installed, you can run SALVE.

However, because OptParse is deprecated in Python 3.x, SALVE depends upon
``argparse``.

To run SALVE with Python 2.6, you will need to install the ``argparse``
package, or do a ``pip`` or ``easy_install`` of ``salve`` to pull in the
dependency automatically.
