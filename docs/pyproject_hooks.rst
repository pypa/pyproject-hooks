``pyproject_hooks``
===================

.. autoclass:: pyproject_hooks.BuildBackendHookCaller
   :special-members: __init__
   :members:

.. _Subprocess Runners:

Subprocess Runners
------------------

A subprocess runner is a function that is expected to execute the subprocess. They are typically used for controlling how output is presented from the subprocess.

The subprocess runners provided out-of-the-box with this library are:

.. autofunction:: pyproject_hooks.default_subprocess_runner(...)
.. autofunction:: pyproject_hooks.quiet_subprocess_runner(...)

Custom Subprocess Runners
^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to provide a custom subprocess runner, that behaves differently. The expected protocol for subprocess runners is as follows:

.. function:: subprocess_runner_protocol(cmd, cwd, extra_environ)
   :noindex:

   :param cmd: The command and arguments to execute, as would be passed to :func:`subprocess.run`.
   :type cmd: list[str]
   :param cwd: The working directory that must be used for the subprocess.
   :type cwd: str
   :param extra_environ: Mapping of environment variables (name to value) which must be set for the subprocess execution.
   :type extra_environ: dict[str, str]

   :rtype: None

Exceptions
----------

Each exception has public attributes with the same name as their constructors.

.. autoexception:: pyproject_hooks.BackendInvalid
.. autoexception:: pyproject_hooks.BackendUnavailable
.. autoexception:: pyproject_hooks.HookMissing
.. autoexception:: pyproject_hooks.UnsupportedOperation
