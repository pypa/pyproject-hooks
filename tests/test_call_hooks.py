import os
from os.path import dirname, abspath, join as pjoin
import tarfile
from testpath import modified_env, assert_isfile
from testpath.tempdir import TemporaryDirectory, TemporaryWorkingDirectory
import pytest
import toml
import zipfile
import sys

from mock import Mock

from pep517.wrappers import Pep517HookCaller, default_subprocess_runner
from pep517.wrappers import UnsupportedOperation, BackendUnavailable


if sys.version_info[0] == 2:
    FileNotFoundError = IOError


SAMPLES_DIR = pjoin(dirname(abspath(__file__)), 'samples')
BUILDSYS_PKGS = pjoin(SAMPLES_DIR, 'buildsys_pkgs')


def get_hooks(pkg, **kwargs):
    source_dir = pjoin(SAMPLES_DIR, pkg)
    with open(pjoin(source_dir, 'pyproject.toml')) as f:
        data = toml.load(f)
    return Pep517HookCaller(
        source_dir, data['build-system']['build-backend'], **kwargs
    )


def test_missing_backend_gives_exception():
    hooks = get_hooks('pkg1')
    with modified_env({'PYTHONPATH': ''}):
        with pytest.raises(BackendUnavailable):
            hooks.get_requires_for_build_wheel({})


def test_get_requires_for_build_wheel():
    hooks = get_hooks('pkg1')
    with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
        res = hooks.get_requires_for_build_wheel({})
    assert res == ['wheelwright']


def test_get_requires_for_build_sdist():
    hooks = get_hooks('pkg1')
    with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
        res = hooks.get_requires_for_build_sdist({})
    assert res == ['frog']


def test_prepare_metadata_for_build_wheel():
    hooks = get_hooks('pkg1')
    with TemporaryDirectory() as metadatadir:
        with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
            hooks.prepare_metadata_for_build_wheel(metadatadir, {})

        assert_isfile(pjoin(metadatadir, 'pkg1-0.5.dist-info', 'METADATA'))


def test_build_wheel():
    hooks = get_hooks('pkg1')
    with TemporaryDirectory() as builddir:
        with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
            whl_file = hooks.build_wheel(builddir, {})

        assert whl_file.endswith('.whl')
        assert os.sep not in whl_file

        whl_file = pjoin(builddir, whl_file)
        assert_isfile(whl_file)
        assert zipfile.is_zipfile(whl_file)


def test_build_wheel_relpath():
    hooks = get_hooks('pkg1')
    with TemporaryWorkingDirectory() as builddir:
        with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
            whl_file = hooks.build_wheel('.', {})

        assert whl_file.endswith('.whl')
        assert os.sep not in whl_file

        whl_file = pjoin(builddir, whl_file)
        assert_isfile(whl_file)
        assert zipfile.is_zipfile(whl_file)


def test_build_sdist():
    hooks = get_hooks('pkg1')
    with TemporaryDirectory() as sdistdir:
        with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
            sdist = hooks.build_sdist(sdistdir, {})

        assert sdist.endswith('.tar.gz')
        assert os.sep not in sdist

        sdist = pjoin(sdistdir, sdist)
        assert_isfile(sdist)
        assert tarfile.is_tarfile(sdist)

        with tarfile.open(sdist) as tf:
            contents = tf.getnames()
        assert 'pkg1-0.5/pyproject.toml' in contents


def test_build_sdist_unsupported():
    hooks = get_hooks('pkg1')
    with TemporaryDirectory() as sdistdir:
        with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
            with pytest.raises(UnsupportedOperation):
                hooks.build_sdist(sdistdir, {'test_unsupported': True})


def test_runner_replaced_on_exception(monkeypatch):
    monkeypatch.setenv('PYTHONPATH', BUILDSYS_PKGS)

    runner = Mock(wraps=default_subprocess_runner)
    hooks = get_hooks('pkg1', runner=runner)

    hooks.get_requires_for_build_wheel()
    runner.assert_called_once()
    runner.reset_mock()

    runner2 = Mock(wraps=default_subprocess_runner)
    try:
        with hooks.subprocess_runner(runner2):
            hooks.get_requires_for_build_wheel()
            runner2.assert_called_once()
            runner2.reset_mock()
            raise RuntimeError()
    except RuntimeError:
        pass

    hooks.get_requires_for_build_wheel()
    runner.assert_called_once()


def test_custom_python_executable(monkeypatch, tmpdir):
    monkeypatch.setenv('PYTHONPATH', BUILDSYS_PKGS)

    runner = Mock(autospec=default_subprocess_runner)
    hooks = get_hooks('pkg1', runner=runner, python_executable='some-python')

    with hooks.subprocess_runner(runner):
        with pytest.raises(FileNotFoundError):
            # output.json is missing because we didn't actually run the hook
            hooks.get_requires_for_build_wheel()
        runner.assert_called_once()
        assert runner.call_args[0][0][0] == 'some-python'
