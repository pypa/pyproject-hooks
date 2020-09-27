`PEP 517 <https://www.python.org/dev/peps/pep-0517/>`_ specifies a standard
API for systems which build Python packages.

This package contains wrappers around the hooks specified by PEP 517. It
provides:

- A mechanism to call the hooks in a subprocess, so they are isolated from
  the current process.
- Fallbacks for the optional hooks, so that frontends can call the hooks without
  checking which are defined.
- Functions to load the build system table from ``pyproject.toml``, with
  optional fallback to setuptools.

Run the tests with ``pytest`` or `tox <https://pypi.org/project/tox>`_.

Usage:

.. code-block:: python

    import os
    from pep517 import Pep517HookCaller
    from pep517.pyproject import load_system

    src = 'path/to/source'  # Folder containing 'pyproject.toml'
    build_sys = load_system(src)

    print(build_sys['requires'])  # List of static requirements

    hooks = Pep517HookCaller(
        src, 
        build_backend=build_sys['build-backend'],
        backend_path=build_sys.get('backend-path'),
    )

    config_options = {}   # Optional parameters for backend
    # List of dynamic requirements:
    print(hooks.get_requires_for_build_wheel(config_options))

    destination = 'also/a/folder'
    whl_filename = hooks.build_wheel(destination, config_options)
    assert os.path.isfile(os.path.join(destination, whl_filename))

The caller is responsible for installing build dependencies.
The static requirements should be installed before trying to call any hooks.

The ``buildtool_demo`` package in this repository gives a more complete
example of how to use the hooks. This is an example, and doesn't get installed
with the ``pep517`` package.
