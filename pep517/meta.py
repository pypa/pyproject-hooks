"""Build metadata for a project using PEP 517 hooks.
"""
import argparse
import logging
import os
import io
import shutil
import zipfile
import functools

try:
    import importlib.metadata as imp_meta
except ImportError:
    import importlib_metadata as imp_meta

try:
    from zipfile import Path
except ImportError:
    from zipp import Path

from .envbuild import BuildEnvironment
from .wrappers import Pep517HookCaller
from .dirtools import tempdir, mkdir_p
from .build import validate_system, load_system, compat_system

log = logging.getLogger(__name__)


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


def build(source_dir='.', dest=None, system=None):
    system = system or load_system(source_dir)
    dest = os.path.join(source_dir, dest or 'dist')
    mkdir_p(dest)
    validate_system(system)
    hooks = Pep517HookCaller(source_dir, system['build-backend'])

    with BuildEnvironment() as env:
        env.pip_install(system['requires'])
        _prep_meta(hooks, env, dest)


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
    return zip_file


def build_as_zip(builder=build):
    with tempdir() as out_dir:
        builder(dest=out_dir)
        return dir_to_zipfile(out_dir)


def load(root):
    """
    Load the metadata from root.

    Return an importlib.metadata.Distribution object.
    """
    root = os.path.expanduser(root)
    system = compat_system(root)
    builder = functools.partial(build, source_dir=root, system=system)
    path = Path(build_as_zip(builder))
    return imp_meta.PathDistribution(path)


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
    build(args.source_dir, args.out_dir)


if __name__ == '__main__':
    main()
