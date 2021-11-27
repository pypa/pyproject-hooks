import tarfile
import zipfile
from os.path import abspath, dirname
from os.path import join as pjoin
from unittest.mock import call, patch

from testpath import assert_isfile, modified_env
from testpath.tempdir import TemporaryDirectory

from pep517.envbuild import BuildEnvironment, build_sdist, build_wheel

SAMPLES_DIR = pjoin(dirname(abspath(__file__)), 'samples')
BUILDSYS_PKGS = pjoin(SAMPLES_DIR, 'buildsys_pkgs')


@patch.object(BuildEnvironment, 'pip_install')
def test_build_wheel(mock_pip_install):
    with modified_env({'PYTHONPATH': BUILDSYS_PKGS}), \
            TemporaryDirectory() as outdir:
        filename = build_wheel(pjoin(SAMPLES_DIR, 'pkg1'), outdir)
        assert_isfile(pjoin(outdir, filename))
        assert zipfile.is_zipfile(pjoin(outdir, filename))

    assert mock_pip_install.call_count == 2
    assert mock_pip_install.call_args_list[0] == call(['eg_buildsys'])
    assert mock_pip_install.call_args_list[1] == call(['wheelwright'])


@patch.object(BuildEnvironment, 'pip_install')
def test_build_sdist(mock_pip_install):
    with modified_env({'PYTHONPATH': BUILDSYS_PKGS}), \
            TemporaryDirectory() as outdir:
        filename = build_sdist(pjoin(SAMPLES_DIR, 'pkg1'), outdir)
        assert_isfile(pjoin(outdir, filename))
        assert tarfile.is_tarfile(pjoin(outdir, filename))

    assert mock_pip_install.call_count == 2
    assert mock_pip_install.call_args_list[0] == call(['eg_buildsys'])
    assert mock_pip_install.call_args_list[1] == call(['frog'])
