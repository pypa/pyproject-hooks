API to call PEP 517 hooks
=========================

`PEP 517 <https://www.python.org/dev/peps/pep-0517/>`_ specifies a standard
API for systems which build Python packages.

`PEP 660 <https://www.python.org/dev/peps/pep-0660/>`_ extends it with a build
mode that leads to editable installs.

This package contains wrappers around the hooks specified by PEP 517 and
PEP 660. It provides:

- A mechanism to call the hooks in a subprocess, so they are isolated from
  the current process.
- Fallbacks for the optional hooks, so that frontends can call the hooks without
  checking which are defined.

Run the tests with ``pytest`` or `tox <https://pypi.org/project/tox>`_.

Usage—you are responsible for ensuring build requirements are available:

.. code-block:: python

    import os
    try:
        import tomllib  # Python >= 3.11 - standard library
    except ImportError:
        import tomli as tomllib  # Python <= 3.10

    from pyproject_hooks import BuildBackendHookCaller

    src = 'path/to/source'  # Folder containing 'pyproject.toml'
    with open(os.path.join(src, 'pyproject.toml'), 'rb') as f:
        build_sys = tomllib.load(f)['build-system']

    print(build_sys['requires'])  # List of static requirements
    # The caller is responsible for installing these and running the hooks in
    # an environment where they are available.

    hooks = BuildBackendHookCaller(
        src,
        build_backend=build_sys['build-backend'],
        backend_path=build_sys.get('backend-path'),
    )

    config_options = {}   # Optional parameters for backend
    # List of dynamic requirements:
    print(hooks.get_requires_for_build_wheel(config_options))
    # Again, the caller is responsible for installing these build requirements

    destination = 'also/a/folder'
    whl_filename = hooks.build_wheel(destination, config_options)
    assert os.path.isfile(os.path.join(destination, whl_filename))
