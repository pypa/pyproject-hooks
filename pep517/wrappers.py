from contextlib import contextmanager
import os
from os.path import dirname, abspath, join as pjoin
import pytoml
import shutil
from subprocess import check_call
import sys
from tempfile import mkdtemp

from . import compat

_in_proc_script = pjoin(dirname(abspath(__file__)), '_in_process.py')

@contextmanager
def tempdir():
    td = mkdtemp()
    try:
        yield td
    finally:
        shutil.rmtree(td)

class UnsupportedOperation(Exception):
    """May be raised by build_sdist if the backend indicates that it can't."""

class Pep517HookCaller(object):
    """A wrapper around a source directory to be built with a PEP 517 backend.

    source_dir : The path to the source directory, containing pyproject.toml.
    """
    def __init__(self, source_dir):
        self.source_dir = abspath(source_dir)
        with open(pjoin(source_dir, 'pyproject.toml')) as f:
            self.pyproject_data = pytoml.load(f)
        buildsys = self.pyproject_data['build-system']
        self.build_sys_requires = buildsys['requires']
        self.build_backend = buildsys['build-backend']

    def get_requires_for_build_wheel(self, config_settings):
        """Identify packages required for building a wheel

        Returns a list of dependency specifications, e.g.:
            ["wheel >= 0.25", "setuptools"]

        This does not include requirements specified in pyproject.toml.
        It returns the result of calling the equivalently named hook in a
        subprocess.
        """
        return self._call_hook('get_requires_for_build_wheel', {
            'config_settings': config_settings
        })

    def prepare_metadata_for_build_wheel(self, metadata_directory, config_settings):
        """Prepare a *.dist-info folder with metadata for this project.

        Returns the name of the newly created folder.

        If the build backend defines a hook with this name, it will be called
        in a subprocess. If not, the backend will be asked to build a wheel,
        and the dist-info extracted from that.
        """
        return self._call_hook('prepare_metadata_for_build_wheel', {
            'metadata_directory': abspath(metadata_directory),
            'config_settings': config_settings,
        })

    def build_wheel(self, wheel_directory, config_settings, metadata_directory=None):
        """Build a wheel from this project.

        Returns the name of the newly created file.

        In general, this will call the 'build_wheel' hook in the backend.
        However, if that was previously called by
        'prepare_metadata_for_build_wheel', and the same metadata_directory is
        used, the previously built wheel will be copied to wheel_directory.
        """
        if metadata_directory is not None:
            metadata_directory = abspath(metadata_directory)
        return self._call_hook('build_wheel', {
            'wheel_directory': abspath(wheel_directory),
            'config_settings': config_settings,
            'metadata_directory': metadata_directory,
        })

    def get_requires_for_build_sdist(self, config_settings):
        """Identify packages required for building a wheel

        Returns a list of dependency specifications, e.g.:
            ["setuptools >= 26"]

        This does not include requirements specified in pyproject.toml.
        It returns the result of calling the equivalently named hook in a
        subprocess.
        """
        return self._call_hook('get_requires_for_build_sdist', {
            'config_settings': config_settings
        })

    def build_sdist(self, sdist_directory, config_settings):
        """Build an sdist from this project.

        Returns the name of the newly created file.

        This calls the 'build_sdist' backend hook in a subprocess.
        """
        return self._call_hook('build_sdist', {
            'sdist_directory': abspath(sdist_directory),
            'config_settings': config_settings,
        })


    def _call_hook(self, hook_name, kwargs):
        env = os.environ.copy()
        env['PEP517_BUILD_BACKEND'] = self.build_backend
        with tempdir() as td:
            compat.write_json({'kwargs': kwargs}, pjoin(td, 'input.json'),
                              indent=2)

            # Run the hook in a subprocess
            check_call([sys.executable, _in_proc_script, hook_name, td],
                       cwd=self.source_dir, env=env)

            data = compat.read_json(pjoin(td, 'output.json'))
            if data.get('unsupported'):
                raise UnsupportedOperation
            return data['return_val']

