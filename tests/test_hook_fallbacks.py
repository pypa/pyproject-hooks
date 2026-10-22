from os.path import abspath, dirname
from os.path import join as pjoin
from unittest.mock import Mock

import pytest
from testpath import assert_isfile, modified_env
from testpath.tempdir import TemporaryDirectory

from pyproject_hooks import BuildBackendHookCaller, HookMissing
from pyproject_hooks._in_process import _in_process
from tests.compat import tomllib

SAMPLES_DIR = pjoin(dirname(abspath(__file__)), "samples")
BUILDSYS_PKGS = pjoin(SAMPLES_DIR, "buildsys_pkgs")


def get_hooks(pkg):
    source_dir = pjoin(SAMPLES_DIR, pkg)
    with open(pjoin(source_dir, "pyproject.toml"), "rb") as f:
        data = tomllib.load(f)
    return BuildBackendHookCaller(source_dir, data["build-system"]["build-backend"])


def test_get_requires_for_build_wheel():
    hooks = get_hooks("pkg2")
    with modified_env({"PYTHONPATH": BUILDSYS_PKGS}):
        res = hooks.get_requires_for_build_wheel({})
    assert res == []


@pytest.mark.parametrize(
    "package,prepare_hook,build_hook",
    [
        ("pkg2", "prepare_metadata_for_build_wheel", "build_wheel"),
        ("pkg3", "prepare_metadata_for_build_editable", "build_editable"),
    ],
)
def test_fallback_reuses_wheel_in_path_with_brackets(
    tmp_path, monkeypatch, package, prepare_hook, build_hook
):
    hooks = get_hooks(package)
    metadata_dir = tmp_path / "metadata[1]"
    metadata_dir.mkdir()
    wheel_dir = tmp_path / "wheels"
    wheel_dir.mkdir()
    with modified_env({"PYTHONPATH": BUILDSYS_PKGS}):
        dist_info = getattr(hooks, prepare_hook)(str(metadata_dir), {})

    # Reusing the cached wheel must not call the backend hook again.
    backend = Mock()
    getattr(backend, build_hook).side_effect = AssertionError("backend called again")
    monkeypatch.setattr(_in_process, "_build_backend", lambda: backend)
    wheel = getattr(_in_process, build_hook)(
        str(wheel_dir), {}, str(metadata_dir / dist_info)
    )
    getattr(backend, build_hook).assert_not_called()
    assert (wheel_dir / wheel).is_file()


def test_get_requires_for_build_editable():
    hooks = get_hooks("pkg2")
    with modified_env({"PYTHONPATH": BUILDSYS_PKGS}):
        res = hooks.get_requires_for_build_editable({})
    assert res == []


def test_get_requires_for_build_sdist():
    hooks = get_hooks("pkg2")
    with modified_env({"PYTHONPATH": BUILDSYS_PKGS}):
        res = hooks.get_requires_for_build_sdist({})
    assert res == []


def test_prepare_metadata_for_build_wheel():
    hooks = get_hooks("pkg2")
    with TemporaryDirectory() as metadatadir:
        with modified_env({"PYTHONPATH": BUILDSYS_PKGS}):
            hooks.prepare_metadata_for_build_wheel(metadatadir, {})

        assert_isfile(pjoin(metadatadir, "pkg2-0.5.dist-info", "METADATA"))


def test_prepare_metadata_for_build_editable():
    hooks = get_hooks("pkg3")
    with TemporaryDirectory() as metadatadir:
        with modified_env({"PYTHONPATH": BUILDSYS_PKGS}):
            hooks.prepare_metadata_for_build_editable(metadatadir, {})

        assert_isfile(pjoin(metadatadir, "pkg3-0.5.dist-info", "METADATA"))


def test_prepare_metadata_for_build_editable_missing_build_editable():
    hooks = get_hooks("pkg2")
    with TemporaryDirectory() as metadatadir:
        with modified_env({"PYTHONPATH": BUILDSYS_PKGS}):
            # pkg2's build system does not have build_editable
            with pytest.raises(HookMissing) as exc_info:
                hooks.prepare_metadata_for_build_editable(metadatadir, {})

            e = exc_info.value
            assert "build_editable" == e.hook_name
            assert "build_editable" == str(e)


def test_prepare_metadata_for_build_wheel_no_fallback():
    hooks = get_hooks("pkg2")

    with TemporaryDirectory() as metadatadir:
        with modified_env({"PYTHONPATH": BUILDSYS_PKGS}):
            with pytest.raises(HookMissing) as exc_info:
                hooks.prepare_metadata_for_build_wheel(
                    metadatadir, {}, _allow_fallback=False
                )

            e = exc_info.value
            assert "prepare_metadata_for_build_wheel" == e.hook_name
            assert "prepare_metadata_for_build_wheel" in str(e)


def test_prepare_metadata_for_build_editable_no_fallback():
    hooks = get_hooks("pkg2")

    with TemporaryDirectory() as metadatadir:
        with modified_env({"PYTHONPATH": BUILDSYS_PKGS}):
            with pytest.raises(HookMissing) as exc_info:
                hooks.prepare_metadata_for_build_editable(
                    metadatadir, {}, _allow_fallback=False
                )

            e = exc_info.value
            assert "prepare_metadata_for_build_editable" == e.hook_name
            assert "prepare_metadata_for_build_editable" in str(e)
