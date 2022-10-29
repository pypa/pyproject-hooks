API reference
=============

.. module:: pyproject_hooks

Calling the build system
------------------------

.. autoclass:: BuildBackendHookCaller

   .. automethod:: get_requires_for_build_sdist

   .. automethod:: get_requires_for_build_wheel

   .. automethod:: get_requires_for_build_editable

   .. automethod:: prepare_metadata_for_build_wheel

   .. automethod:: prepare_metadata_for_build_editable

   .. automethod:: build_sdist

   .. automethod:: build_wheel

   .. automethod:: build_editable

   .. automethod:: subprocess_runner

Subprocess runners
------------------

These functions may be provided when creating :class:`BuildBackendHookCaller`,
or to :meth:`BuildBackendHookCaller.subprocess_runner`.

.. autofunction:: default_subprocess_runner

.. autofunction:: quiet_subprocess_runner

Exceptions
----------

.. autoexception:: BackendUnavailable

.. autoexception:: BackendInvalid

.. autoexception:: HookMissing

.. autoexception:: UnsupportedOperation
