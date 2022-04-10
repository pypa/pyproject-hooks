# SPDX-FileCopyrightText: 2017-2021 Thomas Kluyver <thomas@kluyver.me.uk> and other contributors  # noqa: E501
#
# SPDX-License-Identifier: MIT

from buildsys_minimal import build_sdist, build_wheel  # noqa

build_editable = build_wheel
