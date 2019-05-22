from __future__ import unicode_literals, absolute_import, division

import re

import pytest

from pep517 import meta


@pytest.mark.xfail(
    'sys.version_info < (3,)',
    reason="pep517 cannot be built on Python 2",
)
def test_meta_for_this_package():
    dist = meta.load('.')
    assert re.match(r'[\d.]+', dist.version)
    assert dist.metadata['Name'] == 'pep517'


def test_classic_package(tmpdir):
    (tmpdir / 'setup.py').write_text(
        'from distutils.core import setup; setup(name="foo", version="1.0")',
        encoding='utf-8',
    )
    dist = meta.load(str(tmpdir))
    assert dist.version == '1.0'
    assert dist.metadata['Name'] == 'foo'
