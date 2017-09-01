from contextlib import contextmanager
import io
import json
import os
from os.path import dirname, abspath, join as pjoin
import pytoml
import shutil
from subprocess import check_call
import sys
from tempfile import mkdtemp

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
    def __init__(self, source_dir):
        self.source_dir = source_dir
        with open(pjoin(source_dir, 'pyproject.toml')) as f:
            self.pyproject_data = pytoml.load(f)
        buildsys = self.pyproject_data['build-system']
        self.build_sys_requires = buildsys['requires']
        self.build_backend = buildsys['build-backend']

    def get_build_wheel_requires(self, config_settings):
        return self._call_hook('get_build_wheel_requires', {
            'config_settings': config_settings
        })

    def prepare_wheel_metadata(self, metadata_directory, config_settings):
        return self._call_hook('prepare_wheel_metadata', {
            'metadata_directory': metadata_directory,
            'config_settings': config_settings,
        })

    def build_wheel(self, wheel_directory, config_settings, metadata_directory=None):
        return self._call_hook('build_wheel', {
            'wheel_directory': wheel_directory,
            'config_settings': config_settings,
            'metadata_directory': metadata_directory,
        })

    def get_build_sdist_requires(self, config_settings):
        return self._call_hook('get_build_sdist_requires', {
            'config_settings': config_settings
        })

    def build_sdist(self, sdist_directory, config_settings):
        return self._call_hook('build_sdist', {
            'sdist_directory': sdist_directory,
            'config_settings': config_settings,
        })


    def _call_hook(self, hook_name, kwargs):
        env = os.environ.copy()
        env['PEP517_BUILD_BACKEND'] = self.build_backend
        with tempdir() as td:
            with io.open(pjoin(td, 'input.json'), 'w', encoding='utf-8') as f:
                json.dump({'kwargs': kwargs}, f, indent=True)

            # Run the hook in a subprocess
            check_call([sys.executable, _in_proc_script, hook_name, td],
                       cwd=self.source_dir, env=env)

            output_file = pjoin(td, 'output.json')
            with io.open(output_file, encoding='utf-8') as f:
                data = json.load(f)
            if data.get('unsupported'):
                raise UnsupportedOperation
            return data['return_val']

