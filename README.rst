PEP517
======

`PEP 517 <https://www.python.org/dev/peps/pep-0517/>`_ specifies a standard
API for systems which build Python packages.

This package contains wrappers around the hooks specified by PEP 517. It
provides:

- A mechanism to call the hooks in a subprocess, so they are isolated from
  the current process.
- Fallbacks for the optional hooks, so that frontends can call the hooks without
  checking which are defined.
- Higher-level functions which install the build dependencies into a
  temporary environment and build a wheel/sdist using them.

Run the tests with ``py.test``.

Building a wheel or sdist
-------------------------

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

Lower level usage—you are responsible for ensuring build requirements are
available:

.. code-block:: python

    import os
    import pytoml
    from pep517.wrappers import Pep517HookCaller

    src = 'path/to/source'  # Folder containing 'pyproject.toml'
    with open(os.path.join(src, 'pyproject.toml')) as f:
        build_sys = pytoml.load(f)['build-system']

    print(build_sys['requires'])  # List of static requirements

    hooks = Pep517HookCaller(src, build_backend=build_sys['build_backend'])

    config_options = {}   # Optional parameters for backend
    # List of dynamic requirements:
    print(hooks.get_requires_for_build_wheel(config_options))

    destination = 'also/a/folder'
    whl_filename = hooks.build_wheel(destination, config_options)
    assert os.path.isfile(os.path.join(destination, whl_filename))


Extract metadata
----------------

PEP517 contains highlevel wrappers to extract various metadata.

.. code-block:: python

   # Getting package name from pip reference:

   from pep517.metadata import get_package_name
   print(get_package_name("pillow"))
   # Outputs: "Pillow" (note the spelling!)


   # Getting package dependencies:

   from pep517.metadata import get_package_dependencies
   print(get_package_dependencies("pep517"))
   # Outputs: "['pytoml']"


   # Get package name from arbitrary package source:

   from pep517.metadata import get_package_name
   print(get_package_name("/some/local/project/folder/"))
   # Outputs package name


Build backend tests and more
----------------------------

To test the build backend for a project, run in a system shell:

.. code-block:: shell

    python3 -m pep517.check path/to/source  # source dir containing pyproject.toml

To build a backend into source and/or binary distributions, run in a shell:

.. code-block:: shell

    python -m pep517.build path/to/source  # source dir containing pyproject.toml

This 'build' module should be considered experimental while the PyPA `decides
on the best place for this functionality
<https://github.com/pypa/packaging-problems/issues/219>`_.
