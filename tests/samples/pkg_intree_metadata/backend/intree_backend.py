from importlib.metadata import distribution


def get_requires_for_build_sdist(config_settings):
    dist = distribution("_test_bootstrap")  # discovered in backend-path
    ep = next(iter(dist.entry_points))
    return [ep.group, ep.name, ep.value]
