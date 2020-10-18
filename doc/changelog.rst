Changelog
=========

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
