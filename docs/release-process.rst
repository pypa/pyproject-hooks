===============
Release Process
===============

Actual mechanics of making the release:

- Update the changelog manually, and commit the changes.
- Install :pypi:`bump2version`::

    pip install bump2version

- Run it to bump the version strings within the project, like::

    bump2version minor

- Push the commit and tags to GitHub.
  A GitHub action will upload the release to PyPI.
