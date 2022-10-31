from os.path import abspath, dirname
from os.path import join as pjoin

import pytest
from testpath import assert_isfile, modified_env
from testpath.tempdir import TemporaryDirectory

from pyproject_hooks import BuildBackendHookCaller, HookMissing
from pyproject_hooks._compat import tomllib

SAMPLES_DIR = pjoin(dirname(abspath(__file__)), 'samples')
BUILDSYS_PKGS = pjoin(SAMPLES_DIR, 'buildsys_pkgs')


def get_hooks(pkg):
    source_dir = pjoin(SAMPLES_DIR, pkg)
    with open(pjoin(source_dir, 'pyproject.toml'), 'rb') as f:
        data = tomllib.load(f)
    return BuildBackendHookCaller(source_dir, data['build-system']['build-backend'])


def test_get_requires_for_build_wheel():
    hooks = get_hooks('pkg2')
    with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
        res = hooks.get_requires_for_build_wheel({})
    assert res == []


def test_get_requires_for_build_editable():
    hooks = get_hooks('pkg2')
    with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
        res = hooks.get_requires_for_build_editable({})
    assert res == []


def test_get_requires_for_build_sdist():
    hooks = get_hooks('pkg2')
    with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
        res = hooks.get_requires_for_build_sdist({})
    assert res == []


def test_prepare_metadata_for_build_wheel():
    hooks = get_hooks('pkg2')
    with TemporaryDirectory() as metadatadir:
        with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
            hooks.prepare_metadata_for_build_wheel(metadatadir, {})

        assert_isfile(pjoin(metadatadir, 'pkg2-0.5.dist-info', 'METADATA'))


def test_prepare_metadata_for_build_editable():
    hooks = get_hooks('pkg3')
    with TemporaryDirectory() as metadatadir:
        with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
            hooks.prepare_metadata_for_build_editable(metadatadir, {})

        assert_isfile(pjoin(metadatadir, 'pkg3-0.5.dist-info', 'METADATA'))


def test_prepare_metadata_for_build_editable_missing_build_editable():
    hooks = get_hooks('pkg2')
    with TemporaryDirectory() as metadatadir:
        with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
            # pkg2's build system does not have build_editable
            with pytest.raises(HookMissing) as exc_info:
                hooks.prepare_metadata_for_build_editable(metadatadir, {})

            e = exc_info.value
            assert 'build_editable' == e.hook_name
            assert 'build_editable' == str(e)


def test_prepare_metadata_for_build_wheel_no_fallback():
    hooks = get_hooks('pkg2')

    with TemporaryDirectory() as metadatadir:
        with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
            with pytest.raises(HookMissing) as exc_info:
                hooks.prepare_metadata_for_build_wheel(
                    metadatadir, {}, _allow_fallback=False
                )

            e = exc_info.value
            assert 'prepare_metadata_for_build_wheel' == e.hook_name
            assert 'prepare_metadata_for_build_wheel' in str(e)


def test_prepare_metadata_for_build_editable_no_fallback():
    hooks = get_hooks('pkg2')

    with TemporaryDirectory() as metadatadir:
        with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
            with pytest.raises(HookMissing) as exc_info:
                hooks.prepare_metadata_for_build_editable(
                    metadatadir, {}, _allow_fallback=False
                )

            e = exc_info.value
            assert 'prepare_metadata_for_build_editable' == e.hook_name
            assert 'prepare_metadata_for_build_editable' in str(e)
