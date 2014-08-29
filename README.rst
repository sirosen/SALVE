.. image:: https://travis-ci.org/sirosen/SALVE.svg?branch=stable
    :alt: Build Status
    :target: https://travis-ci.org/sirosen/SALVE
.. image:: https://coveralls.io/repos/sirosen/SALVE/badge.png?branch=stable
    :alt: Coverage Status
    :target: https://coveralls.io/r/sirosen/SALVE?branch=stable
.. image:: https://badge.fury.io/py/salve.svg
    :alt: PyPi Version
    :target: https://badge.fury.io/py/salve

SALVE
=====

Authors: Stephen Rosen

Version: 2.3.0

More information is available at `SALVE Website`_.

.. _SALVE Website:
    http://salve.sirosen.net/

What can it do?
===============

SALVE versions files and directories in a git repository, and handles the messy process of deploying those files onto a machine.
It is safer to use than shell scripts in a few ways, and guarantees idempotence for a wide class of deployment actions.
It also backs up the preexisting versions of files that it changes when possible so that you can recover them if necessary at a later date.

To start writing manifests, you can go to the `Quick-Start Guide`_.
For a more detailed description of the SALVE language, the `Language Page`_ and the `Examples Page`_ are good resources.

.. _Quick-Start Guide:
    http://salve.sirosen.net/quickstart.html
.. _Language Page:
    http://salve.sirosen.net/lang.html
.. _Examples Page:
    http://salve.sirosen.net/examples.html

What do I need to run it?
=========================

SALVE is fully compatible with Python 2.7, 3.2, 3.3, and 3.4

It has no dependencies on python packages, so as long as you have one of these
versions of Python installed, you can run SALVE.

Roadmap
=======

These are the features and fixes currently in the pipeline for SALVE.
Generally Fixes are prioritized over Features, depending on their severity.

Features
--------
 - Plugin framework
 - Variable and attribute definition in manifest blocks to propogate down the block tree as defaults
 - Automatic file backup recovery using dates, generation numbers, and so forth

Fixes
-----
 - ``~`` and ``*`` expansion does not offer useful error messages.
 - Verification is performed on a rolling basis, rather than once at the start of execution
 - Dir alterations (chown/chmod) are based on walks at generation time, not execution time
