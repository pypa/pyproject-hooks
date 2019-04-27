from os.path import dirname, abspath, join as pjoin
import pytoml
from testpath import modified_env
import pytest

from pep517.wrappers import Pep517HookCaller, BackendInvalid

SAMPLES_DIR = pjoin(dirname(abspath(__file__)), 'samples')
BUILDSYS_PKGS = pjoin(SAMPLES_DIR, 'buildsys_pkgs')


def get_hooks(pkg, backend=None, path=None):
    source_dir = pjoin(SAMPLES_DIR, pkg)
    with open(pjoin(source_dir, 'pyproject.toml')) as f:
        data = pytoml.load(f)
    if backend is None:
        backend = data['build-system']['build-backend']
    if path is None:
        path = data['build-system']['backend-path']
    return Pep517HookCaller(source_dir, backend, path)


def test_backend_path_within_tree():
    source_dir = pjoin(SAMPLES_DIR, 'pkg1')
    assert Pep517HookCaller(source_dir, 'dummy', ['.', 'subdir'])
    assert Pep517HookCaller(source_dir, 'dummy', ['../pkg1', 'subdir/..'])
    # TODO: Do we want to insist on ValueError, or invent another exception?
    with pytest.raises(Exception):
        assert Pep517HookCaller(source_dir, 'dummy', [source_dir])
    with pytest.raises(Exception):
        Pep517HookCaller(source_dir, 'dummy', ['.', '..'])
    with pytest.raises(Exception):
        Pep517HookCaller(source_dir, 'dummy', ['subdir/../..'])
    with pytest.raises(Exception):
        Pep517HookCaller(source_dir, 'dummy', ['/'])


def test_intree_backend():
    hooks = get_hooks('pkg_intree')
    with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
        res = hooks.get_requires_for_build_sdist({})
    assert res == ["intree_backend_called"]


def test_intree_backend_not_in_path():
    hooks = get_hooks('pkg_intree', backend='buildsys')
    with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
        with pytest.raises(BackendInvalid):
            hooks.get_requires_for_build_sdist({})
