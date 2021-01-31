import sys
from setuptools import setup
from os import path, environ, listdir
import json

children = listdir(sys.path[0])
out = path.join(environ['PEP517_ISSUE104_OUTDIR'], 'out.json')
with open(out, 'w') as f:
    json.dump(children, f)

setup()
