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
    from pep517.wrappers import Pep517HookCaller

    src = 'path/to/source'  # Folder containing 'pyproject.toml'
    hooks = Pep517HookCaller(src)
    print(hooks.build_sys_requires)  # List of static requirements

    config_options = {}   # Optional parameters for backend
    # List of dynamic requirements:
    print(hooks.get_requires_for_build_wheel(config_options))

    destination = 'also/a/folder'
    whl_filename = hooks.build_wheel(destination, config_options)
    assert os.path.isfile(os.path.join(destination, whl_filename))
