# SPDX-FileCopyrightText: 2017-2021 Thomas Kluyver <thomas@kluyver.me.uk> and other contributors  # noqa: E501
#
# SPDX-License-Identifier: MIT

"""This is a subpackage because the directory is on sys.path for _in_process.py

The subpackage should stay as empty as possible to avoid shadowing modules that
the backend might import.
"""
from contextlib import contextmanager
from os.path import abspath, dirname
from os.path import join as pjoin

try:
    import importlib.resources as resources

    def _in_proc_script_path():
        return resources.path(__package__, '_in_process.py')
except ImportError:
    @contextmanager
    def _in_proc_script_path():
        yield pjoin(dirname(abspath(__file__)), '_in_process.py')
