# SPDX-FileCopyrightText: 2017-2021 Thomas Kluyver <thomas@kluyver.me.uk> and other contributors  # noqa: E501
#
# SPDX-License-Identifier: MIT

from os.path import abspath, dirname
from os.path import join as pjoin

import pytest
import tomli
from testpath import modified_env

from pep517.wrappers import BackendInvalid, Pep517HookCaller

SAMPLES_DIR = pjoin(dirname(abspath(__file__)), 'samples')
BUILDSYS_PKGS = pjoin(SAMPLES_DIR, 'buildsys_pkgs')
SOURCE_DIR = pjoin(SAMPLES_DIR, 'pkg1')


def get_hooks(pkg, backend=None, path=None):
    source_dir = pjoin(SAMPLES_DIR, pkg)
    with open(pjoin(source_dir, 'pyproject.toml'), 'rb') as f:
        data = tomli.load(f)
    if backend is None:
        backend = data['build-system']['build-backend']
    if path is None:
        path = data['build-system']['backend-path']
    return Pep517HookCaller(source_dir, backend, path)


@pytest.mark.parametrize('backend_path', [
    ['.', 'subdir'],
    ['../pkg1', 'subdir/..'],
])
def test_backend_path_within_tree(backend_path):
    Pep517HookCaller(SOURCE_DIR, 'dummy', backend_path)


@pytest.mark.parametrize('backend_path', [
    [SOURCE_DIR],
    ['.', '..'],
    ['subdir/../..'],
    ['/'],
])
def test_backend_out_of_tree(backend_path):
    # TODO: Do we want to insist on ValueError, or invent another exception?
    with pytest.raises(Exception):
        Pep517HookCaller(SOURCE_DIR, 'dummy', backend_path)


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
