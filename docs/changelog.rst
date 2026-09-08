Changelog
=========

v1.3
----

- Python 3.8 or above is now required (:pr:`214`).
- Forward warnings from the backend to the frontend (:pr:`213`).
- Show the traceback from the backend on a ``BackendUnavailable`` error (:pr:`219`).
- Fix the return type annotation for ``prepare_metadata_for_build_wheel``
  (:pr:`209`).
- Fix removing the internal ``_in_process`` directory from ``sys.path`` where
  the install location includes a symlink (:pr:`230`).
- Use ``os.path.commonpath`` instead of the deprecated ``commonprefix`` to
  validate the location of in-tree backends.
- Fix in-tree backends in locations containing the path separator character -
  ``:`` on Posix platforms, ``;`` on Windows (:pr:`232`).
- Fix finding distribution metadata with ``importlib.metadata`` in the backend
  when an in-tree backend is used (:pr:`212`).
- ``pyproject_hooks`` can be built from source using flit_core 4.x (:pr:`233`).
- Document that the ``hooks.subprocess_runner`` context manager API is not
  thread-safe (:pr:227`)

v1.2
----

- Improve interoperability with ``importlib.metadata``, fixing a regression
  in setuptools compatibility in 1.1 (PR :pr:`199`).
- Clean up the ``_in_process`` directory inside the package from ``sys.path``
  before imporing the backend (PR :pr:`193`).

v1.1
----

- Add type annotations to the public API.
- More careful handling of the ``backend-path`` key from ``pyproject.toml``.
  Previous versions would load the backend and then check that it was loaded
  from the specified path; the new version only loads it from the specified path.
  The ``BackendInvalid`` exception is now a synonym for :exc:`BackendUnavailable`,
  and code should move to using the latter name.

v1.0
----

- Rename package to ``pyproject_hooks`` (from ``pep517``).
- Remove deprecated modules (``.build``, ``.check`` and ``.envbuild``).
  Use the `build <https://pypa-build.readthedocs.io/en/stable/>`_ project
  instead for this higher-level functionality of setting up a temporary build
  environment.
- Require Python 3.7 or above.
- Use ``tomllib`` from the standard library on Python 3.11. ``pyproject_hooks``
  now has no external dependencies when installed in Python 3.11.
- Avoid chaining exceptions when using the fallback implementation for
  :meth:`.prepare_metadata_for_build_wheel`.
- Fix propagating error message for :exc:`.BackendInvalid` errors.

v0.13
-----

- Remove support for end-of-life Pythons. Now requires Python3.6+.
- Remove support for ``toml`` package. Now requires ``tomli``.
- Rely on preferred "files" API on Python 3.9 and later (:issue:`140`).

v0.12
-----

- Add method for pip to check if build_editable hook is supported.
  This is a private API for now.

v0.11.1
-------

- Fix DeprecationWarning in tomli.

v0.11
-----

- Support editable hooks (`PEP 660 <https://www.python.org/dev/peps/pep-0660/>`_).
- Use the TOML 1.0 compliant ``tomli`` parser module on Python 3.6 and above.
- Ensure TOML files are always read as UTF-8.
- Switch CI to Github actions.

v0.10
-----

- Avoid shadowing imports such as ``colorlog`` in the backend, by moving the
  ``_in_process.py`` script into a separate subpackage.
- Issue warnings when using the deprecated ``pep517.build`` and
  ``pep517.check`` modules at the command line. See the `PyPA build project
  <https://github.com/pypa/build>`_ for a replacement.
- Allow building with flit_core 3.x.
- Prefer the standard library ``unittest.mock`` to ``mock`` for tests on Python
  3.6 and above.

v0.9.1
------

- Silence some static analysis warnings.

v0.9
-----

- Deprecated the higher level API which handles creating an environment and
  installing build dependencies. This was not very complete, and the `PyPA build
  project <https://github.com/pypa/build>`_ is designed for this use case.
- New ``python_executable`` parameter for :class:`.BuildBackendHookCaller` to run hooks
  with a different Python interpreter.
- Fix for locating the script to run in the subprocess in some scenarios.
- Fix example in README to get ``build-backend`` correctly.
- Created `documentation on Read the Docs
  <https://pep517.readthedocs.io/en/latest/index.html>`__
- Various minor improvements to testing.
