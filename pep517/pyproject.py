import os

import toml

from .compat import FileNotFoundError

__all__ = [
    'validate_system',
    'load_system',
    'compat_system',
]


def validate_system(system):
    """
    Ensure build system has the requisite fields.
    """
    required = {'requires', 'build-backend'}
    if not (required <= set(system)):
        message = "Missing required fields: {missing}".format(
            missing=required-set(system),
        )
        raise ValueError(message)


def load_system(source_dir):
    """
    Load the build system from a source dir (pyproject.toml).
    """
    pyproject = os.path.join(source_dir, 'pyproject.toml')
    with open(pyproject) as f:
        pyproject_data = toml.load(f)
    return pyproject_data['build-system']


def compat_system(source_dir):
    """
    Given a source dir, attempt to get a build system backend
    and requirements from pyproject.toml. Fallback to
    setuptools but only if the file was not found or a build
    system was not indicated.
    """
    try:
        system = load_system(source_dir)
    except (FileNotFoundError, KeyError):
        system = {}
    system.setdefault(
        'build-backend',
        'setuptools.build_meta:__legacy__',
    )
    system.setdefault('requires', ['setuptools', 'wheel'])
    return system
