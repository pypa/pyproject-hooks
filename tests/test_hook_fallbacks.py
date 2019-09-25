from os.path import dirname, abspath, join as pjoin
import pytest
import toml
from testpath import modified_env, assert_isfile
from testpath.tempdir import TemporaryDirectory

from pep517.wrappers import HookMissing, Pep517HookCaller

SAMPLES_DIR = pjoin(dirname(abspath(__file__)), 'samples')
BUILDSYS_PKGS = pjoin(SAMPLES_DIR, 'buildsys_pkgs')


def get_hooks(pkg):
    source_dir = pjoin(SAMPLES_DIR, pkg)
    with open(pjoin(source_dir, 'pyproject.toml')) as f:
        data = toml.load(f)
    return Pep517HookCaller(source_dir, data['build-system']['build-backend'])


def test_get_requires_for_build_wheel():
    hooks = get_hooks('pkg2')
    with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
        res = hooks.get_requires_for_build_wheel({})
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
