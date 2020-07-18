=========
treecrawl
=========


.. image:: https://img.shields.io/pypi/v/treecrawl.svg
        :target: https://pypi.python.org/pypi/treecrawl

.. image:: https://img.shields.io/travis/natemarks/treecrawl.svg
        :target: https://travis-ci.com/natemarks/treecrawl

.. image:: https://readthedocs.org/projects/treecrawl/badge/?version=latest
        :target: https://treecrawl.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




libraries to make it easier to maniuplate files in a directory tree


* Free software: MIT license
* Documentation: https://treecrawl.readthedocs.io.


Features
--------

* DirEdit: Base class used to transform contents of a directory tree
* TestData: Helper class for testing directories edited by DirEdit

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage


Build Notes
------------

Pipenv cna't pi the setuptools and pip versions so we ned to manually update them in the pvirtual environment.  These are the upload the a new version:

::

    python -m venv .treecrawl.venv
    source .treecrawl.venv/bin/activate
    pip install -r requirements-dev.txt

