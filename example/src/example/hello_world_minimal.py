#! /usr/local/bin/python3
"""Minimal hello-world example using VersionReporter."""

# Copyright (c) 2026 Tom Björkholm
# MIT License


import argparse
import sys
from datetime import date
from typing import Optional

from packaging.version import Version

from versionreporter import VersionReporter


class MinimalHelloVersionReporter(VersionReporter):
    """Report version information for the minimal hello-world example."""

    def package_names(self) -> list[str]:
        """Return the package names that this example reports."""
        # In a real application, the first item would be your own PyPI project
        # name so VersionReporter can read its installed version and check
        # whether PyPI has a newer release of it.
        # This example script is only a source file in the repository, so it
        # does not have its own published PyPI package name.
        # We therefore use the already installed 'build' package as a stand-in
        # application name so the example can still demonstrate the full
        # VersionReporter workflow, including searching PyPI for newer
        # available versions.
        return ['build', 'versionreporter', 'packaging']

    def get_app_support_expires(self) -> dict[date, str]:
        """Return when this example would stop supporting older Python."""
        return {date(year=2027, month=1, day=1): '3.12',
                date(year=2028, month=1, day=1): '3.13'}

    @classmethod
    def get_main_package_name(cls) -> str:
        """Return the package treated as the main application package."""
        # Matching the first name from package_names() keeps the upgrade
        # instructions in the printed report easy to understand.
        return 'build'

    @classmethod
    def recommended_python(cls) -> Version:
        """Return the Python version this example recommends."""
        return Version('3.13')


def version_requested(argv: Optional[list[str]] = None) -> bool:
    """Return whether the command line requested version information."""
    desc = 'Minimal hello world example using VersionReporter.'
    parser = argparse.ArgumentParser(prog='hello_world_minimal',
                                     description=desc)
    help_text = 'Show the VersionReporter table instead of the ' \
                'hello message.'
    parser.add_argument('--version', dest='show_version', default=False,
                        action='store_true', help=help_text)
    parsed_arguments = parser.parse_args(argv)
    return bool(parsed_arguments.show_version)


def main(argv: Optional[list[str]] = None) -> int:
    """Run the minimal hello-world example application."""
    if version_requested(argv):
        MinimalHelloVersionReporter().print()
        return 0
    print('Hello, world!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
