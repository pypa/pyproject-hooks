"""Automation using nox.
"""

import nox

nox.options.reuse_existing_virtualenvs = True


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12", "3.13", "pypy3"])
def test(session: nox.Session) -> None:
    session.install("-r", "dev-requirements.txt")
    session.install(".")
    session.run("pytest", *session.posargs)


@nox.session
def docs(session: nox.Session) -> None:
    session.install("-e", ".")
    session.install("-r", "docs/requirements.txt")

    session.run(
        "sphinx-build",
        "-W",
        "-d=docs/_build/doctrees/html",
        "-b=dirhtml",
        "docs/",
        "docs/_build/html",
    )


@nox.session
def lint(session: nox.Session) -> None:
    session.install("pre-commit")

    if session.posargs:
        args = session.posargs + ["--all-files"]
    else:
        args = ["--all-files", "--show-diff-on-failure"]

    session.run("pre-commit", "run", *args)


@nox.session
def release(session: nox.Session) -> None:
    session.install("flit")
    session.run("flit", "publish")
