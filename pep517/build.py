"""Build a project using PEP 517 hooks.
"""
import argparse
import logging
import os
import contextlib
import pytoml
import shutil
import errno
import tempfile

from .envbuild import BuildEnvironment
from .wrappers import Pep517HookCaller

log = logging.getLogger(__name__)


@contextlib.contextmanager
def tempdir():
    td = tempfile.mkdtemp()
    try:
        yield td
    finally:
        shutil.rmtree(td)


def _do_build(hooks, env, dist, dest):
    get_requires_name = 'get_requires_for_build_{dist}'.format(**locals())
    get_requires = getattr(hooks, get_requires_name)
    reqs = get_requires({})
    log.info('Got build requires: %s', reqs)

    env.pip_install(reqs)
    log.info('Installed dynamic build dependencies')

    with tempdir() as td:
        log.info('Trying to build %s in %s', dist, td)
        build_name = 'build_{dist}'.format(**locals())
        build = getattr(hooks, build_name)
        filename = build(td, {})
        source = os.path.join(td, filename)
        shutil.move(source, os.path.join(dest, os.path.basename(filename)))


def mkdir_p(*args, **kwargs):
    """Like `mkdir`, but does not raise an exception if the
    directory already exists.
    """
    try:
        return os.mkdir(*args, **kwargs)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise


def build(source_dir, dist):
    pyproject = os.path.join(source_dir, 'pyproject.toml')
    dest = os.path.join(source_dir, 'dist')
    mkdir_p(dest)

    with open(pyproject) as f:
        pyproject_data = pytoml.load(f)
    # Ensure the mandatory data can be loaded
    buildsys = pyproject_data['build-system']
    requires = buildsys['requires']
    backend = buildsys['build-backend']

    hooks = Pep517HookCaller(source_dir, backend)

    with BuildEnvironment() as env:
        env.pip_install(requires)
        _do_build(hooks, env, dist, dest)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument(
        'source_dir',
        help="A directory containing pyproject.toml",
    )
    ap.add_argument(
        '--binary',
        action='store_true',
        default=False,
    )
    ap.add_argument(
        '--source',
        action='store_true',
        default=False,
    )
    args = ap.parse_args(argv)

    # determine which dists to build
    dists = list(filter(None, (
        'sdist' if args.source or not args.binary else None,
        'wheel' if args.binary or not args.source else None,
    )))

    for dist in dists:
        build(args.source_dir, dist)


if __name__ == '__main__':
    main()
