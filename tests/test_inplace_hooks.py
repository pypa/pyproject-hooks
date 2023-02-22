from inspect import cleandoc
from os.path import abspath, dirname
from os.path import join as pjoin
from pathlib import Path

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


def test_intree_backend():
    hooks = get_hooks("pkg_intree")
    with modified_env({"PYTHONPATH": BUILDSYS_PKGS}):
        res = hooks.get_requires_for_build_sdist({})
    assert res == ["intree_backend_called"]


def test_intree_backend_not_in_path():
    hooks = get_hooks("pkg_intree", backend="buildsys")
    with modified_env({"PYTHONPATH": BUILDSYS_PKGS}):
        msg = "Cannot find module 'buildsys' in .*pkg_intree.*backend"
        with pytest.raises(BackendUnavailable, match=msg):
            hooks.get_requires_for_build_sdist({})


def test_intree_backend_loaded_from_correct_backend_path():
    """
    PEP 517 establishes that the backend code should be loaded from ``backend-path``,
    and recognizes that not always the environment isolation is perfect
    (e.g. it explicitly mentions ``--system-site-packages``). Therefore, even in a
    situation where a ``MetaPathFinder`` would have priority to find the backend spec,
    the backend should still be loaded from ``backend-path``.
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
