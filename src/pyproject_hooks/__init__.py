"""Wrappers to call pyproject.toml-based build backend hooks.
"""

from typing import TYPE_CHECKING

from ._impl import (
    BackendInvalid,
    BackendUnavailable,
    BuildBackendHookCaller,
    HookMissing,
    UnsupportedOperation,
    default_subprocess_runner,
    quiet_subprocess_runner,
)

__version__ = "1.0.0"
__all__ = [
    "BackendUnavailable",
    "BackendInvalid",
    "HookMissing",
    "UnsupportedOperation",
    "default_subprocess_runner",
    "quiet_subprocess_runner",
    "BuildBackendHookCaller",
]

if TYPE_CHECKING:
    from ._impl import SubprocessRunner  # noqa: F401

    __all__.append("SubprocessRunner")
