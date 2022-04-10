# SPDX-FileCopyrightText: 2017-2021 Thomas Kluyver <thomas@kluyver.me.uk> and other contributors
#
# SPDX-License-Identifier: MIT

import json
import sys
from os import environ, listdir, path

from setuptools import setup

children = listdir(sys.path[0])
out = path.join(environ['PEP517_ISSUE104_OUTDIR'], 'out.json')
with open(out, 'w') as f:
    json.dump(children, f)

setup()
