# A "bootstrap backend" for testing purposes
def get_requires_for_build_wheel(*args, **kwargs):
    return ['wheel', 'sentinel']


def get_requires_for_build_sdist(*args, **kwargs):
    return ['sdist_sentinel']


def prepare_metadata_for_build_wheel(*args, **kwargs):
    pass


def build_wheel(*args, **kwargs):
    pass


def build_sdist(*args, **kwargs):
    pass
