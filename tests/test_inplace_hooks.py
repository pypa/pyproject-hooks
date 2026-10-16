import os
from inspect import cleandoc
from os import pathsep
from os.path import abspath, dirname
from os.path import join as pjoin
from pathlib import Path
from shutil import copytree

import pytest
from testpath import modified_env
from testpath.tempdir import TemporaryDirectory

from pyproject_hooks import BackendUnavailable, BuildBackendHookCaller
from tests.compat import tomllib

SAMPLES_DIR = pjoin(dirname(abspath(__file__)), "samples")
BUILDSYS_PKGS = pjoin(SAMPLES_DIR, "buildsys_pkgs")
SOURCE_DIR = pjoin(SAMPLES_DIR, "pkg1")


def get_hooks(pkg, backend=None, path=None):
    source_dir = pjoin(SAMPLES_DIR, pkg)
    with open(pjoin(source_dir, "pyproject.toml"), "rb") as f:
        data = tomllib.load(f)
    if backend is None:
        backend = data["build-system"]["build-backend"]
    if path is None:
        path = data["build-system"]["backend-path"]
    return BuildBackendHookCaller(source_dir, backend, path)


@pytest.mark.parametrize(
    "backend_path",
    [
        [".", "subdir"],
        ["../pkg1", "subdir/.."],
    ],
)
def test_backend_path_within_tree(backend_path):
    BuildBackendHookCaller(SOURCE_DIR, "dummy", backend_path)


@pytest.mark.parametrize(
    "backend_path",
    [
        [SOURCE_DIR],
        [".", ".."],
        ["subdir/../.."],
        ["/"],
    ],
)
def test_backend_out_of_tree(backend_path):
    # TODO: Do we want to insist on ValueError, or invent another exception?
    with pytest.raises(Exception):
        BuildBackendHookCaller(SOURCE_DIR, "dummy", backend_path)


def test_backend_path_symlink_outside_tree(tmp_path):
    source_tree = tmp_path / "project"
    source_tree.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    _directory_symlink_or_skip(source_tree / "backend", outside)

    with pytest.raises(ValueError, match="paths must be inside source tree"):
        BuildBackendHookCaller(source_tree, "dummy", ["backend"])


def test_backend_path_symlink_inside_tree_preserves_path(tmp_path):
    source_tree = tmp_path / "project"
    source_tree.mkdir()
    backend_target = source_tree / "actual-backend"
    backend_target.mkdir()
    backend_link = source_tree / "backend"
    _directory_symlink_or_skip(backend_link, backend_target)

    hooks = BuildBackendHookCaller(source_tree, "dummy", ["backend"])

    expected = os.path.normpath(os.path.abspath(os.path.join(source_tree, "backend")))
    assert hooks.backend_path == [expected]


def test_backend_path_with_symlinked_source_root_preserves_path(tmp_path):
    source_tree = tmp_path / "actual-project"
    source_tree.mkdir()
    (source_tree / "backend").mkdir()
    source_link = tmp_path / "project-link"
    _directory_symlink_or_skip(source_link, source_tree)

    hooks = BuildBackendHookCaller(source_link, "dummy", ["backend"])

    expected = os.path.normpath(os.path.abspath(os.path.join(source_link, "backend")))
    assert hooks.backend_path == [expected]


def _directory_symlink_or_skip(link, target):
    try:
        link.symlink_to(target, target_is_directory=True)
    except (NotImplementedError, OSError) as exc:
        pytest.skip(f"directory symlink creation is unavailable: {exc}")


@pytest.mark.parametrize("example", ("pkg_intree", "pkg_nested_intree"))
def test_intree_backend(example):
    hooks = get_hooks(example)
    with modified_env({"PYTHONPATH": BUILDSYS_PKGS}):
        res = hooks.get_requires_for_build_sdist({})
    assert res == ["intree_backend_called"]


def test_intree_backend_path_containing_path_separator(tmp_path):
    source_dir = tmp_path / f"project{pathsep}{pathsep}source"
    copytree(Path(SAMPLES_DIR, "pkg_intree"), source_dir)
    hooks = BuildBackendHookCaller(source_dir, "intree_backend", ["backend"])

    assert hooks.get_requires_for_build_sdist({}) == ["intree_backend_called"]


@pytest.mark.parametrize("backend", ("buildsys", "nested.buildsys"))
def test_intree_backend_not_in_path(backend):
    hooks = get_hooks("pkg_intree", backend=backend)
    with modified_env({"PYTHONPATH": BUILDSYS_PKGS}):
        msg = f"Cannot find module {backend!r} in .*pkg_intree.*backend"
        with pytest.raises(BackendUnavailable, match=msg):
            hooks.get_requires_for_build_sdist({})


def test_intree_backend_loaded_from_correct_backend_path():
    """
    PEP 517 establishes that the backend code should be loaded from ``backend-path``,
    and recognizes that not always the environment isolation is perfect
    (e.g. it explicitly mentions ``--system-site-packages``).
    Therefore, even in a situation where a third-party ``MetaPathFinder`` has
    precedence over ``importlib.machinery.PathFinder``, the backend should
    still be loaded from ``backend-path``.
    """
    hooks = get_hooks("pkg_intree", backend="intree_backend")
    with TemporaryDirectory() as tmp:
        invalid = Path(tmp, ".invalid", "intree_backend.py")
        invalid.parent.mkdir()
        invalid.write_text("raise ImportError('Do not import')", encoding="utf-8")
        install_finder_with_sitecustomize(tmp, {"intree_backend": str(invalid)})
        with modified_env({"PYTHONPATH": tmp}):  # Override `sitecustomize`.
            res = hooks.get_requires_for_build_sdist({})
    assert res == ["intree_backend_called"]


def test_intree_backend_importlib_metadata_interoperation():
    pytest.importorskip("importlib.metadata")

    hooks = get_hooks("pkg_intree_metadata", backend="intree_backend")
    assert hooks.get_requires_for_build_sdist({}) == [
        "_test_backend.importlib_metadata",
        "hello",
        "world",
    ]


def test_distribution_mismatch():
    pytest.importorskip("importlib.metadata")

    hooks = get_hooks("distribution_mismatch")
    assert hooks.get_requires_for_build_sdist({}) != ["0.0.1"]


def install_finder_with_sitecustomize(directory, mapping):
    finder = f"""
        import sys
        from importlib.util import spec_from_file_location

        MAPPING = {mapping!r}

        class _Finder:  # MetaPathFinder
            @classmethod
            def find_spec(cls, fullname, path=None, target=None):
                if fullname in MAPPING:
                    return spec_from_file_location(fullname, MAPPING[fullname])

        def install():
            if not any(finder == _Finder for finder in sys.meta_path):
                sys.meta_path.insert(0, _Finder)
    """
    sitecustomize = "import _test_finder_; _test_finder_.install()"
    Path(directory, "_test_finder_.py").write_text(cleandoc(finder), encoding="utf-8")
    Path(directory, "sitecustomize.py").write_text(sitecustomize, encoding="utf-8")
