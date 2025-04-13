"""Test "backend" defining nothing other than a hook that logs a warning.
"""

import warnings


def get_requires_for_build_wheel(config_settings):
    warnings.warn("this is my example warning")
    return []
