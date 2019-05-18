"""Build metadata for a project using PEP 517 hooks.
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


def _prep_meta(hooks, env, dest):
    reqs = hooks.get_requires_for_build_wheel({})
    log.info('Got build requires: %s', reqs)

    env.pip_install(reqs)
    log.info('Installed dynamic build dependencies')

    with tempdir() as td:
        log.info('Trying to build metadata in %s', td)
        filename = hooks.prepare_metadata_for_build_wheel(td, {})
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


def build_meta(source_dir, dest=None):
    pyproject = os.path.join(source_dir, 'pyproject.toml')
    dest = os.path.join(source_dir, dest or 'dist')
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
        _prep_meta(hooks, env, dest)


parser = argparse.ArgumentParser()
parser.add_argument(
    'source_dir',
    help="A directory containing pyproject.toml",
)
parser.add_argument(
    '--out-dir', '-o',
    help="Destination in which to save the builds relative to source dir",
)


def main():
    args = parser.parse_args()
    build_meta(args.source_dir, args.out_dir)


if __name__ == '__main__':
    main()
