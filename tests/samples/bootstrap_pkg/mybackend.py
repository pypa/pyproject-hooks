# A "bootstrap backend" for testing purposes
def get_requires_for_build_wheel(config_settings=None):
    return ['wheel', 'sentinel']


def get_requires_for_build_sdist(config_settings=None):
    return ['sdist_sentinel']


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    pass


def build_wheel(wheel_directory, config_settings=None,
                metadata_directory=None):
    pass


def build_sdist(sdist_directory, config_settings):
    pass
