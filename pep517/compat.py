"""Python 2/3 compatibility"""
import io
import json
import sys


# Handle reading JSON in any encoding
# and writing JSON in utf8, on Python 3 and 2.

if sys.version_info >= (3, 6) or sys.version_info <= (2,):

    # python3.6 restored support for loading json bytes
    def read_json(path):
        with io.open(path, 'rb') as f:
            return json.load(f)

else:
    # python 3.5
    def read_json(path):
        with io.open(path, 'r', encoding="utf8") as f:
            return json.load(f)

if sys.version_info >= (3,):

    def write_json(obj, path, **kwargs):
        with io.open(path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, **kwargs)

else:

    def write_json(obj, path, **kwargs):
        with io.open(path, 'wb') as f:
            json.dump(obj, f, encoding='utf-8', **kwargs)


# FileNotFoundError

try:
    FileNotFoundError = FileNotFoundError
except NameError:
    FileNotFoundError = IOError


if sys.version_info < (3, 6):
    from toml import load as _toml_load  # noqa: F401

    def toml_load(f):
        w = io.TextIOWrapper(f, encoding="utf8", newline="")
        try:
            return _toml_load(w)
        finally:
            w.detach()

    from toml import TomlDecodeError as TOMLDecodeError  # noqa: F401
else:
    from tomli import load as toml_load  # noqa: F401
    from tomli import TOMLDecodeError  # noqa: F401
