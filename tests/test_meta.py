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
