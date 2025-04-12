import json
import sys
from os import environ, path

from setuptools import setup

captured_sys_path = sys.path
out = path.join(environ["TEST_POLLUTION_OUTDIR"], "out.json")
with open(out, "w") as f:
    json.dump(captured_sys_path, f)

setup()
