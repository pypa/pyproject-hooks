`PEP 517 <https://www.python.org/dev/peps/pep-0517/>`_ specifies a standard
API for systems which build Python packages.

This package contains a wrapper around the hooks specified by PEP 517. It
provides:

- A mechanism to call the hooks in a subprocess, so they are isolated from
  the current process.
- Fallbacks for the optional hooks, so that frontends can call the hooks without
  checking which are defined.

Run the tests with ``py.test``.
