from os.path import dirname, abspath, join as pjoin
from testpath import modified_env
from pep517.wrappers import Pep517HookCaller

SAMPLES_DIR = pjoin(dirname(abspath(__file__)), 'samples')
BUILDSYS_PKGS = pjoin(SAMPLES_DIR, 'buildsys_pkgs')

def test_get_build_wheel_requires():
    hooks = Pep517HookCaller(pjoin(SAMPLES_DIR, 'pkg1'))
    with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
        res = hooks.get_build_wheel_requires({})
    assert res == ['wheelwright']

def test_get_build_sdist_requires():
    hooks = Pep517HookCaller(pjoin(SAMPLES_DIR, 'pkg1'))
    with modified_env({'PYTHONPATH': BUILDSYS_PKGS}):
        res = hooks.get_build_sdist_requires({})
    assert res == ['frog']
