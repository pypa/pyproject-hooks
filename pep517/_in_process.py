"""This is invoked in a subprocess to call the build backend hooks.

It expects:
- Command line args: hook_name, control_dir
- Environment variable: PEP517_BUILD_BACKEND=entry.point:spec
- control_dir/input.json:
  - {"kwargs": {...}}

Results:
- control_dir/output.json
  - {"return_val": ...}
"""
from glob import glob
from importlib import import_module
import io
import json
import os
from os.path import join as pjoin
import re
import shutil
import sys
import tempfile

def _build_backend():
    """Find and load the build backend"""
    ep = os.environ['PEP517_BUILD_BACKEND']
    mod_path, _, obj_path = ep.partition(':')
    obj = import_module(mod_path)
    if obj_path:
        for path_part in obj_path.split('.'):
            obj = getattr(obj, path_part)
    return obj

def get_build_wheel_requires(config_settings):
    """Invoke the optional get_build_wheel_requires hook
    
    Returns [] if the hook is not defined.
    """
    backend = _build_backend()
    try:
        hook = backend.get_build_wheel_requires
    except AttributeError:
        return []
    else:
        return hook(config_settings)

def prepare_wheel_metadata(metadata_directory, config_settings):
    """Invoke optional prepare_wheel_metadata
    
    Implements a fallback by building a wheel if the hook isn't defined.
    """
    backend = _build_backend()
    try:
        hook = backend.prepare_wheel_metadata
    except AttributeError:
        return _get_wheel_metadata_from_wheel(backend, metadata_directory,
                                              config_settings)
    else:
        return hook(metadata_directory, config_settings)

WHEEL_BUILT_MARKER = 'PEP517_ALREADY_BUILT_WHEEL'

def _dist_info_files(whl_zip):
    """Identify the .dist-info folder inside a wheel ZipFile."""
    res = []
    for path in whl_zip.namelist():
        m = re.match(r'[^/\\]+-[^/\\]+\.dist-info/', path)
        if m:
            res.append(path)
    if res:
        return res
    raise Exception("No .dist-info folder found in wheel")

def _get_wheel_metadata_from_wheel(backend, metadata_directory, config_settings):
    """Build a wheel and extract the metadata from it.
    
    Fallback for when the build backend does not define the 'get_wheel_metadata'
    hook.
    """
    from zipfile import ZipFile
    whl_basename = backend.build_wheel(metadata_directory, config_settings)
    with open(os.path.join(metadata_directory, WHEEL_BUILT_MARKER), 'wb'):
        pass  # Touch marker file

    whl_file = os.path.join(metadata_directory, whl_basename)
    with ZipFile(whl_file) as zipf:
        dist_info = _dist_info_files(zipf)
        zipf.extractall(path=metadata_directory, members=dist_info)
    return dist_info[0].split('/')[0]

def _find_already_built_wheel(metadata_directory):
    """Check for a wheel already built during the get_wheel_metadata hook.
    """
    if not metadata_directory:
        return None
    metadata_parent = os.path.dirname(metadata_directory)
    if not os.path.isfile(pjoin(metadata_parent, WHEEL_BUILT_MARKER)):
        return None

    whl_files = glob(os.path.join(metadata_parent, '*.whl'))
    if not whl_files:
        print('Found wheel built marker, but no .whl files')
        return None
    if len(whl_files) > 1:
        print('Found multiple .whl files; unspecified behaviour. '
              'Will call build_wheel.')
        return None
    
    # Exactly one .whl file
    return whl_files[0]

def build_wheel(wheel_directory, config_settings, metadata_directory=None):
    """Invoke the mandatory build_wheel hook.
    
    If a wheel was already built in the prepare_wheel_metadata fallback, this
    will copy it rather than rebuilding the wheel.
    """
    prebuilt_whl = _find_already_built_wheel(metadata_directory)
    if prebuilt_whl:
        shutil.copy2(prebuilt_whl, wheel_directory)
        return os.path.basename(prebuilt_whl)

    return _build_backend().build_wheel(wheel_directory, config_settings,
                                        metadata_directory)


def get_build_sdist_requires(config_settings):
    """Invoke the optional get_build_wheel_requires hook

    Returns [] if the hook is not defined.
    """
    backend = _build_backend()
    try:
        hook = backend.get_build_sdist_requires
    except AttributeError:
        return []
    else:
        return hook(config_settings)

class _DummyException(Exception):
    """Nothing should ever raise this exception"""

class GotUnsupportedOperation(Exception):
    """For internal use when backend raises UnsupportedOperation"""

def build_sdist(sdist_directory, config_settings):
    """Invoke the mandatory build_sdist hook."""
    backend = _build_backend()
    try:
        return backend.build_sdist(sdist_directory, config_settings)
    except getattr(backend, 'UnsupportedOperation', _DummyException):
        raise GotUnsupportedOperation

HOOK_NAMES = {
    'get_build_wheel_requires',
    'prepare_wheel_metadata',
    'build_wheel',
    'get_build_sdist_requires',
    'build_sdist',
}

def main():
    if len(sys.argv) < 3:
        sys.exit("Needs args: hook_name, control_dir")
    hook_name = sys.argv[1]
    control_dir = sys.argv[2]
    if hook_name not in HOOK_NAMES:
        sys.exit("Unknown hook: %s" % hook_name)
    hook = globals()[hook_name]
    
    with io.open(pjoin(control_dir, 'input.json'), encoding='utf-8') as f:
        hook_input = json.load(f)

    json_out = {'unsupported': False, 'return_val': None}
    try:
        json_out['return_val'] = hook(**hook_input['kwargs'])
    except GotUnsupportedOperation:
        json_out['unsupported'] = True
    
    with io.open(pjoin(control_dir, 'output.json'), 'w', encoding='utf-8') as f:
        json.dump(json_out, f, indent=2)

if __name__ == '__main__':
    main()
