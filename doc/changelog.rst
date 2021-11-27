Changelog
=========

UNRELEASED
----------

- Remove support for end-of-life Pythons. Now requires Python3.6+.
- Remove support for ``toml`` package. Now requires ``tomli``.

0.12
----

- Add method for pip to check if build_editable hook is supported.
  This is a private API for now.

0.11.1
------

- Fix DeprecationWarning in tomli.

0.11
----

- Support editable hooks (`PEP 660 <https://www.python.org/dev/peps/pep-0660/>`_).
- Use the TOML 1.0 compliant ``tomli`` parser module on Python 3.6 and above.
- Ensure TOML files are always read as UTF-8.
- Switch CI to Github actions.

0.10
----

- Avoid shadowing imports such as ``colorlog`` in the backend, by moving the
  ``_in_process.py`` script into a separate subpackage.
- Issue warnings when using the deprecated ``pep517.build`` and
  ``pep517.check`` modules at the command line. See the `PyPA build project
  <https://github.com/pypa/build>`_ for a replacement.
- Allow building with flit_core 3.x.
- Prefer the standard library ``unittest.mock`` to ``mock`` for tests on Python
  3.6 and above.

0.9.1
-----

- Silence some static analysis warnings.

0.9
---

- Deprecated the higher level API which handles creating an environment and
  installing build dependencies. This was not very complete, and the `PyPA build
  project <https://github.com/pypa/build>`_ is designed for this use case.
- New ``python_executable`` parameter for :class:`.Pep517HookCaller` to run hooks
  with a different Python interpreter.
- Fix for locating the script to run in the subprocess in some scenarios.
- Fix example in README to get ``build-backend`` correctly.
- Created `documentation on Read the Docs
  <https://pep517.readthedocs.io/en/latest/index.html>`__
- Various minor improvements to testing.
