pyproject-hooks
===============

This is a low-level library for calling build-backends in ``pyproject.toml``-based project. It provides the basic functionality to help write tooling that generates distribution files from Python projects.

What this library provides
--------------------------

- Logic for calling build-backend hooks in a subprocess.
- Automated fallbacks for optional build-backend hooks.
- Control over how the subprocesses are run.

What this library does not provide
----------------------------------

- Environment management / isolation

  It is the responsibility of the caller to setup an environment containing the build dependencies, and provide a ``python_executable`` to this library to use that environment. It is also the caller's responsibility to install any "additional" dependencies before calls to certain hooks.

- A command line interface

  This is a low-level library that would simplify writing such an interface but providing a command line interface is out-of-scope for this project.

These roles are covered by tools like `build <https://pypa-build.readthedocs.io/en/stable/>`_, which use this library.

.. toctree::
   :caption: API reference
   :hidden:

   pyproject_hooks

.. toctree::
   :caption: Project
   :hidden:

   changelog
   release-process
