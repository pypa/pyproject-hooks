import re

from pep517 import meta


def test_meta_for_this_package():
    dist = meta.load('.')
    assert re.match(r'[\d.]+', dist.version)
    assert dist.metadata['Name'] == 'pep517'
