"""Test backend defining only the mandatory hooks.

Don't use this for any real code.
"""
from glob import glob
from os.path import join as pjoin
import tarfile
from zipfile import ZipFile


def build_wheel(wheel_directory, config_settings, metadata_directory=None):
    whl_file = 'pkg2-0.5-py2.py3-none-any.whl'
    with ZipFile(pjoin(wheel_directory, whl_file), 'w') as zf:
        for pyfile in glob('*.py'):
            zf.write(pyfile)
        for metadata in glob('*.dist-info/*'):
            zf.write(metadata)
    return whl_file


def build_sdist(sdist_directory, config_settings):
    target = 'pkg2-0.5.tar.gz'
    with tarfile.open(pjoin(sdist_directory, target), 'w:gz',
                      format=tarfile.PAX_FORMAT) as tf:
        def _add(relpath):
            tf.add(relpath, arcname='pkg2-0.5/' + relpath)

        _add('pyproject.toml')
        for pyfile in glob('*.py'):
            _add(pyfile)
        for distinfo in glob('*.dist-info'):
            _add(distinfo)

    return target
