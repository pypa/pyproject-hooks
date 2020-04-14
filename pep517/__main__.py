"""PEP517 command-line script.
"""
import argparse


def configure_build_parser(parser):
    parser.add_argument(
        'source_dir',
        help="A directory containing pyproject.toml",
    )
    parser.add_argument(
        '--binary', '-b',
        action='store_true',
        default=False,
    )
    parser.add_argument(
        '--source', '-s',
        action='store_true',
        default=False,
    )
    parser.add_argument(
        '--out-dir', '-o',
        help="Destination in which to save the builds relative to source dir",
    )


def configure_check_parser(parser):
    parser.add_argument(
        'source_dir',
        help="A directory containing pyproject.toml")


def configure_meta_parser(parser):
    parser.add_argument(
        'source_dir',
        help="A directory containing pyproject.toml",
    )
    parser.add_argument(
        '--out-dir', '-o',
        help="Destination in which to save the builds relative to source dir",
    )


def _run(args):
    if args.command == "build":
        from .build import main
        main(args)
    elif args.command == "check":
        from .check import run
        run(args)
    elif args.command == "meta":
        from .meta import build
        build(args)
    else:
        raise ValueError(args.command)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    build = subparsers.add_parser(
        "build",
        help="Build a project using PEP 517 hooks.",
        description="Build a project using PEP 517 hooks.",
    )
    configure_build_parser(build)
    check = subparsers.add_parser(
        "check",
        help="Check a project and backend by attempting to build using PEP 517 hooks.",
        description="Check a project and backend by attempting to build using PEP 517 hooks.",
    )
    configure_check_parser(check)
    meta = subparsers.add_parser(
        "meta",
        help="Build metadata for a project using PEP 517 hooks.",
        description="Build metadata for a project using PEP 517 hooks.",
    )
    configure_meta_parser(meta)

    args = parser.parse_args()
    _run(args)


if __name__ == "__main__":
    main()
