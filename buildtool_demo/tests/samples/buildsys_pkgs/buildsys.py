"""This is a very stupid backend for testing purposes.

Don't use this for any real code.
"""

from glob import glob
from os.path import join as pjoin
import shutil
import tarfile
from zipfile import ZipFile


def get_requires_for_build_wheel(config_settings):
    return ['wheelwright']


def prepare_metadata_for_build_wheel(metadata_directory, config_settings):
    for distinfo in glob('*.dist-info'):
        shutil.copytree(distinfo, pjoin(metadata_directory, distinfo))


def prepare_build_wheel_files(build_directory, config_settings):
    shutil.copy('pyproject.toml', build_directory)
    for pyfile in glob('*.py'):
        shutil.copy(pyfile, build_directory)
    for distinfo in glob('*.dist-info'):
        shutil.copytree(distinfo, pjoin(build_directory, distinfo))


def build_wheel(wheel_directory, config_settings, metadata_directory=None):
    whl_file = 'pkg1-0.5-py2.py3-none-any.whl'
    with ZipFile(pjoin(wheel_directory, whl_file), 'w') as zf:
        for pyfile in glob('*.py'):
            zf.write(pyfile)
        for metadata in glob('*.dist-info/*'):
            zf.write(metadata)
    return whl_file


def get_requires_for_build_sdist(config_settings):
    return ['frog']


class UnsupportedOperation(Exception):
    pass


def build_sdist(sdist_directory, config_settings):
    if config_settings.get('test_unsupported', False):
        raise UnsupportedOperation

    target = 'pkg1-0.5.tar.gz'
    with tarfile.open(pjoin(sdist_directory, target), 'w:gz',
                      format=tarfile.PAX_FORMAT) as tf:
        def _add(relpath):
            tf.add(relpath, arcname='pkg1-0.5/' + relpath)

        _add('pyproject.toml')
        for pyfile in glob('*.py'):
            _add(pyfile)

    return target
