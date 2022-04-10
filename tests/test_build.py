# SPDX-FileCopyrightText: 2017-2021 Thomas Kluyver <thomas@kluyver.me.uk> and other contributors  # noqa: E501
#
# SPDX-License-Identifier: MIT

import pytest

from pep517 import build


def system(*args):
    return dict.fromkeys(args)


class TestValidateSystem:
    def test_missing(self):
        with pytest.raises(ValueError):
            build.validate_system(system())
        with pytest.raises(ValueError):
            build.validate_system(system('requires'))
        with pytest.raises(ValueError):
            build.validate_system(system('build-backend'))
        with pytest.raises(ValueError):
            build.validate_system(system('other'))

    def test_missing_and_extra(self):
        with pytest.raises(ValueError):
            build.validate_system(system('build-backend', 'other'))

    def test_satisfied(self):
        build.validate_system(system('build-backend', 'requires'))
        build.validate_system(system('build-backend', 'requires', 'other'))
