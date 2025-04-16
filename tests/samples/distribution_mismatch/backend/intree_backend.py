from importlib.metadata import distribution


def get_requires_for_build_sdist(config_settings):
    dist = distribution("setuptools")  # not present in backend-path
    return [dist.version]
