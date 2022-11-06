API reference
=============

.. warning::

   The core of this package (the APIs described below) has been renamed to
   `pyproject-hooks <https://pyproject-hooks.readthedocs.io/>`_. Please use that
   package (low level) or `build <https://pypa-build.readthedocs.io/en/stable/>`_
   (higher level) in place of ``pep517``.

.. module:: pep517

Calling the build system
------------------------

.. autoclass:: Pep517HookCaller

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

These functions may be provided when creating :class:`Pep517HookCaller`,
or to :meth:`Pep517HookCaller.subprocess_runner`.

.. autofunction:: default_subprocess_runner

.. autofunction:: quiet_subprocess_runner

Exceptions
----------

.. autoexception:: BackendUnavailable

.. autoexception:: BackendInvalid

.. autoexception:: HookMissing

.. autoexception:: UnsupportedOperation
