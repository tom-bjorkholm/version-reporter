#! /usr/local/bin/python3
"""Hello-world example showing the early support check pattern."""

# Copyright (c) 2026 Tom Björkholm
# MIT License


import argparse
import sys
from datetime import date
from typing import Optional

from packaging.version import Version

from versionreporter import VersionReporter, SupportExpires


class SupportAwareHelloVersionReporter(VersionReporter):
    """Report versions for the support-aware hello-world example."""

    def package_names(self) -> list[str]:
        """Return the package names that this example reports."""
        # In a real application, this list would start with your own published
        # application package.
        # These teaching examples are not published on PyPI, so PyPI would not
        # know anything about a package named after this script.
        # We therefore use the real 'requests' package as a fake application
        # name. That keeps the example honest about how VersionReporter works:
        # it can only report installed distribution versions and look for newer
        # releases on PyPI when the package names are real PyPI project names.
        return ['requests', 'versionreporter', 'packaging']

    def get_app_support_expires(self) -> SupportExpires:
        """Return when this example would stop supporting older Python."""
        return {date(year=2027, month=6, day=1): '3.12',
                date(year=2028, month=6, day=1): '3.13'}

    @classmethod
    def get_main_package_name(cls) -> str:
        """Return the package treated as the main application package."""
        return 'requests'

    @classmethod
    def recommended_python(cls) -> Version:
        """Return the Python version this example recommends."""
        return Version('3.14')


def build_argument_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the support-aware example."""
    desc = 'Hello world example using VersionReporter.'
    parser = argparse.ArgumentParser(description=desc)
    help_text = 'Name to greet when not printing version information.'
    parser.add_argument('--name', default='world', help=help_text)
    help_text = 'Print application and dependency version information.'
    parser.add_argument('--version', action='store_true', help=help_text)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Run the support-aware hello-world example application."""
    reporter = SupportAwareHelloVersionReporter()
    # This is the other recommended integration point in the API: check near
    # the start of main() whether the running Python version is too old.
    # On a still-supported Python version this prints nothing, so the program
    # simply continues with normal argument parsing and application logic.
    reporter.check_if_unsupported_python()
    args = build_argument_parser().parse_args(argv)
    if args.version:
        reporter.print()
        return 0
    print(f'Hello, {args.name}!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
