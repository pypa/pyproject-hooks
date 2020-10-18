API to call PEP 517 hooks
=========================

`PEP 517 <https://www.python.org/dev/peps/pep-0517/>`_ specifies a standard
API for systems which build Python packages.

This package contains wrappers around the hooks specified by PEP 517. It
provides:

- A mechanism to call the hooks in a subprocess, so they are isolated from
  the current process.
- Fallbacks for the optional hooks, so that frontends can call the hooks without
  checking which are defined.

Run the tests with ``pytest`` or `tox <https://pypi.org/project/tox>`_.

Usage—you are responsible for ensuring build requirements are available:

.. code-block:: python

    import os
    import toml
    from pep517.wrappers import Pep517HookCaller

    src = 'path/to/source'  # Folder containing 'pyproject.toml'
    with open(os.path.join(src, 'pyproject.toml')) as f:
        build_sys = toml.load(f)['build-system']

    print(build_sys['requires'])  # List of static requirements
    # The caller is responsible for installing these and running the hooks in
    # an environment where they are available.

    hooks = Pep517HookCaller(
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

Deprecated high-level
---------------------

For now, ``pep517`` also contains higher-level functions which install the build
dependencies into a temporary environment and build a wheel/sdist using them.
This is a rough implementation, e.g. it does not do proper build isolation.
The `PyPA build project <https://github.com/pypa/build>`_ is recommended as an
alternative, although it's still quite young in October 2020.
This layer of functionality in ``pep517`` is now deprecated, but won't be
removed for some time, as there is code relying on it.

High level usage, with build requirements handled:

.. code-block:: python

    import os
    from pep517.envbuild import build_wheel, build_sdist

    src = 'path/to/source'  # Folder containing 'pyproject.toml'
    destination = 'also/a/folder'
    whl_filename = build_wheel(src, destination)
    assert os.path.isfile(os.path.join(destination, whl_filename))

    targz_filename = build_sdist(src, destination)
    assert os.path.isfile(os.path.join(destination, targz_filename))

To test the build backend for a project, run in a system shell:

.. code-block:: shell

    python3 -m pep517.check path/to/source  # source dir containing pyproject.toml

To build a backend into source and/or binary distributions, run in a shell:

.. code-block:: shell

    python -m pep517.build path/to/source  # source dir containing pyproject.toml

All of this high-level functionality is deprecated.
