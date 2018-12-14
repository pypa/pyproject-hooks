from os.path import dirname, abspath, join as pjoin
import tarfile
from testpath import modified_env, assert_isfile
from testpath.tempdir import TemporaryDirectory
try:
    from unittest.mock import patch, call
except ImportError:
    from mock import patch, call  # Python 2 fallback
import zipfile

from pep517.envbuild import build_sdist, build_wheel, BuildEnvironment

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
