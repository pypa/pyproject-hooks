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

class Pep517HookCaller(object):
    def __init__(self, source_dir):
        self.source_dir = source_dir
        with open(pjoin(source_dir, 'pyproject.toml')) as f:
            self.pyproject_data = pytoml.load(f)
        buildsys = self.pyproject_data['build-system']
        self.build_sys_requires = buildsys['requires']
        self.build_backend = buildsys['build_backend']

    def get_build_requires(self, config_settings):
        return self._call_hook('get_build_requires', {
            'config_settings': config_settings
        })

    def get_wheel_metadata(self, metadata_directory, config_settings):
        return self._call_hook('get_wheel_metadata', {
            'metadata_directory': metadata_directory,
            'config_settings': config_settings,
        })

    def build_wheel(self, wheel_directory, config_settings, metadata_directory=None):
        return self._call_hook('build_wheel', {
            'wheel_directory': wheel_directory,
            'config_settings': config_settings,
            'metadata_directory': metadata_directory,
        })

    def build_sdist(self, sdist_directory, config_settings):
        return self._call_hook('get_wheel_metadata', {
            'sdist_directory': sdist_directory,
            'config_settings': config_settings,
        })

    def prepare_build_files(self, build_directory, config_settings):
        return self._call_hook('prepare_build_files', {
            'build_directory': build_directory,
            'config_settings': config_settings,
        })

    def _call_hook(self, hook_name, kwargs):
        env = os.environ.copy()
        env['PEP517_BUILD_BACKEND'] = self.build_backend
        with tempdir() as td:
            with io.open(pjoin(td, 'input.json'), 'w', encoding='utf-8') as f:
                json.dump({'kwargs': kwargs}, f, indent=True)
            check_call([sys.executable, _in_proc_script, hook_name, td])

            output_file = pjoin(td, 'output.json')
            if os.path.isfile(output_file):
                with io.open(output_file, encoding='utf-8') as f:
                    return json.load(f)['return_val']
            else:
                return None
