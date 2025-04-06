A10SA Script
============

|PyPI| |Status| |Python Version| |License|

|Read the Docs| |Tests| |Codecov|

|pre-commit| |Black|

.. |PyPI| image:: https://img.shields.io/pypi/v/a10sa-script.svg
   :target: https://pypi.org/project/a10sa-script/
   :alt: PyPI
.. |Status| image:: https://img.shields.io/pypi/status/a10sa-script.svg
   :target: https://pypi.org/project/a10sa-script/
   :alt: Status
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/a10sa-script
   :target: https://pypi.org/project/a10sa-script
   :alt: Python Version
.. |License| image:: https://img.shields.io/pypi/l/a10sa-script
   :target: https://opensource.org/licenses/MIT
   :alt: License
.. |Read the Docs| image:: https://img.shields.io/readthedocs/a10sa-script/latest.svg?label=Read%20the%20Docs
   :target: https://a10sa-script.readthedocs.io/
   :alt: Read the documentation at https://a10sa-script.readthedocs.io/
.. |Tests| image:: https://github.com/bhrevol/a10sa-script/workflows/Tests/badge.svg
   :target: https://github.com/bhrevol/a10sa-script/actions?workflow=Tests
   :alt: Tests
.. |Codecov| image:: https://codecov.io/gh/bhrevol/a10sa-script/branch/main/graph/badge.svg
   :target: https://app.codecov.io/gh/bhrevol/a10sa-script
   :alt: Codecov
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit
.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Black

Library for manipulating Vorze A10 sex toy scripts.


Features
--------

* Read/Write/Convert supported script formats.
* Export scripts as `Buttplug Protocol`_ command sequences.

Experimental features
---------------------

**Experimental features are not fully tested, use at your own risk.**

* Control Vorze devices directly via BluetoothLE (tested with CycloneSA, untested for UFOSA, PistonSA).
* Control linear/funscript devices via `Buttplug Protocol`_ (requires `Intiface Central`_, tested with Handy).

*Bluetooth functionality requires installation with ``[ble]`` dependencies.*

.. _Buttplug Protocol: https://buttplug.io/
.. _Intiface Central: https://intiface.com/

Supported Formats
-----------------

* Vorze CSV
* Afesta/LPEG VCSX (``.bin``)
* Funscript JSON


Requirements
------------

* Python 3.10+


Installation
------------

You can install *A10SA Script* via pip_ from PyPI_:

.. code:: console

   $ pip install a10sa-script

Optional dependencies can also be installed to enable experimental feature support:

.. code:: console

    $ pip install a10sa-script[ble]


Usage
-----

Convert VCSX ``Vorze_CycloneSA.bin`` to ``script_cyclone.csv``:

.. code:: py

    >>> from a10sa_script.script import VCSXCycloneScript, VorzeRotateScript
    >>> with open("Vorze_CycloneSA.bin", "rb") as f:
    ...     vcsx = VCSXCycloneScript.load(f)
    >>> with open("script_cyclone.csv", "wb") as f:
    ...     VorzeRotateScript(vcsx.commands).dump(f)

Convert CSV ``script_piston.csv`` to ``script.funscript``:

.. code:: py

    >>> from a10sa_script.script import VorzeLinearScript, FunscriptScript
    >>> with open("script_piston.csv", "rb") as f:
    ...     csv = VorzeLinearScript.load(f)
    >>> with open("script.funscript", "wb") as f:
    ...     FunscriptScript.from_vorze(csv).dump(f)

Convert funscript ``script.funscript`` to ``script_piston.csv``:

.. code:: py

    >>> from a10sa_script.script import VorzeLinearScript, FunscriptScript
    >>> with open("script.funscript", "rb") as f:
    ...     funscript = FunscriptScript.load(f)
    >>> with open("script_piston.csv", "wb") as f:
    ...     funscript.to_vorze().dump(f)

Please see the `Command-line Reference <Usage_>`_ for details.


Contributing
------------

Contributions are very welcome.
To learn more, see the `Contributor Guide`_.


License
-------

Distributed under the terms of the `MIT license`_,
*A10SA Script* is free and open source software.


Issues
------

If you encounter any problems,
please `file an issue`_ along with a detailed description.


Credits
-------

This project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.

.. _@cjolowicz: https://github.com/cjolowicz
.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _MIT license: https://opensource.org/licenses/MIT
.. _PyPI: https://pypi.org/
.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python
.. _file an issue: https://github.com/bhrevol/a10sa-script/issues
.. _pip: https://pip.pypa.io/
.. github-only
.. _Contributor Guide: https://a10sa-script.readthedocs.io/en/latest/contributing.html
.. _Usage: https://a10sa-script.readthedocs.io/en/latest/usage.html
