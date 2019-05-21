import os
import contextlib
import tempfile
import shutil
import errno


@contextlib.contextmanager
def tempdir():
    td = tempfile.mkdtemp()
    try:
        yield td
    finally:
        shutil.rmtree(td)


def mkdir_p(*args, **kwargs):
    """Like `mkdir`, but does not raise an exception if the
    directory already exists.
    """
    try:
        return os.mkdir(*args, **kwargs)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise
