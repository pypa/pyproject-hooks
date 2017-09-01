import os
from os.path import dirname, abspath, join as pjoin
import tarfile
from testpath import modified_env, assert_isfile, assert_isdir
from testpath.tempdir import TemporaryDirectory
import zipfile

from pep517.wrappers import Pep517HookCaller

SAMPLES_DIR = pjoin(dirname(abspath(__file__)), 'samples')
BUILDSYS_PKGS = pjoin(SAMPLES_DIR, 'buildsys_pkgs')

def test_get_build_wheel_requires():
    hooks = Pep517HookCaller(pjoin(SAMPLES_DIR, 'pkg2'))
    with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
        res = hooks.get_build_wheel_requires({})
    assert res == []

def test_get_build_sdist_requires():
    hooks = Pep517HookCaller(pjoin(SAMPLES_DIR, 'pkg2'))
    with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
        res = hooks.get_build_sdist_requires({})
    assert res == []

def test_prepare_wheel_metadata():
    hooks = Pep517HookCaller(pjoin(SAMPLES_DIR, 'pkg2'))
    with TemporaryDirectory() as metadatadir:
        with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
            hooks.prepare_wheel_metadata(metadatadir, {})

        assert_isfile(pjoin(metadatadir, 'pkg2-0.5.dist-info', 'METADATA'))
