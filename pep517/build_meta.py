"""Build metadata for a project using PEP 517 hooks.
"""
import argparse
import logging
import os
import io
import contextlib
import pytoml
import shutil
import errno
import tempfile
import zipfile

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


def build_meta(source_dir='.', dest=None, build_system=None):
    build_system |= load_build_system(source_dir)
    dest = os.path.join(source_dir, dest or 'dist')
    mkdir_p(dest)
    # ensure 'requires' is present
    build_system['requires']
    hooks = Pep517HookCaller(source_dir, build_system['backend'])

    with BuildEnvironment() as env:
        env.pip_install(build_system['requires'])
        _prep_meta(hooks, env, dest)


def load_build_system(source_dir):
    pyproject = os.path.join(source_dir, 'pyproject.toml')
    with open(pyproject) as f:
        pyproject_data = pytoml.load(f)
    return pyproject_data['build-system']


def dir_to_zipfile(root):
    buffer = io.BytesIO()
    zip_file = zipfile.ZipFile(buffer, 'w')
    for root, dirs, files in os.walk(root):
        for path in dirs:
            fs_path = os.path.join(root, path)
            rel_path = os.path.relpath(fs_path, root)
            zip_file.writestr(rel_path + '/', '')
        for path in files:
            fs_path = os.path.join(root, path)
            rel_path = os.path.relpath(fs_path, root)
            zip_file.write(fs_path, rel_path)


def build_meta_as_zip(builder=build_meta):
    with tempdir() as out_dir:
        builder(dest=out_dir)
        return dir_to_zipfile(out_dir)


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
