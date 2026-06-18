#! /usr/local/bin/python3
"""Get and print version information."""

# Copyright (c) 2024-2026 Tom Björkholm
# MIT License


import sys
from importlib.metadata import version as metadata_version
from typing import Optional, NamedTuple
from datetime import date
from pypi_simple import PyPISimple
from pypi_simple.errors import NoSuchProjectError, \
    UnsupportedContentTypeError, UnsupportedRepoVersionError
from requests import HTTPError
from packaging.version import Version
from packaging.requirements import Requirement

type VersionInfo = dict[str, Version]
type SupportExpires = dict[date, str]


class _AvailableVersion(NamedTuple):
    """Information on available versions of a package."""

    is_better_for_pyver: bool
    is_best_for_new_py: bool
    best_ver: Version
    better_ver: Version
    pkgname: str


type _AvailableVersions = list[_AvailableVersion]


class VersionReporter():
    """Get and print version information.

    A class to help an application to easily report version information
    for the application itself and for the most important packages that
    the application uses. The report also includes information about
    the availability of newer versions of the listed packages.

    The application that uses this class shall create a derived class
    and override the methods: `package_names`, `get_app_support_expires`
    `get_recommended_python_version` and `get_main_package_name`
    to specify the packages that the application uses, the dates when
    the application will no longer be supported on a given Python
    version, and the recommended Python version for the application.

    The recommended usage in the application is then to call the `print`
    method of the derived class when a `--version` flag is entered on the
    command line of the application.
    Another recommended usage is to call the `check_if_unsupported_python`
    method early in the application program flow to check if the running
    Python version is no longer supported by the application and print
    an appropriate message to the user.
    """

    def __init__(self) -> None:
        """Create a version reporter object."""
        self.versions: Optional[VersionInfo] = None

    def print(self, versions: Optional[VersionInfo] = None) -> None:
        """Print version information.

        Print version information for the application and the most important
        packages that the application uses. The most common usage of this
        method is to call it when a `--version` flag is entered on the
        command line of the application.

        The version information is printed in a table format with the
        package names and their versions. If there are newer versions
        available for the current Python version, information about these
        is also printed. If there are newer versions available for a newer
        Python version, information about these is also printed.

        Args:
            versions: Optional version information to print. If None,
                      the version information is obtained from the
                      `_get` method.
        """
        if versions is None:
            if self.versions is None:
                self.versions = self._get()
            versions = self.versions
        maxlen: int = max(map(len, versions.keys()))
        for key, value in versions.items():
            pad = '.' * (maxlen - len(key))
            print(f'{key} {pad} {str(value)}')
        self._print_info_on_new_pkgs(versions=versions)
        rec_pyver = self.get_recommended_python_version()
        if 'Python' in versions and versions['Python'] < rec_pyver:
            self._print_upgrade_instruction(versions=versions)

    def check_if_unsupported_python(self) -> None:
        """Check if the Python version is no longer supported by the app.

        This method checks if the running Python version is no longer supported
        by the application and prints an appropriate message to the user.
        The most common usage of this method is to call it early in the
        application program flow.
        """
        running_versions = self._get()
        sup_ends = self.get_app_support_expires()
        now = self._today()
        pyvers = running_versions['Python']
        txt = '\n\nYou are running an old version of Python: ' + str(pyvers)
        txt += '\nThis application no longer releases bug fixes for this old'
        txt += ' Python version.'
        txt += '\nThis application no longer releases new features for this'
        txt += ' old Python version.\n'
        for day, version in sup_ends.items():
            if now >= day:
                cmpvers = Version('.'.join(list(str(s) for s in
                                                pyvers.release[0:2])))
                if cmpvers <= Version(version):
                    print(txt)
                    self._print_upgrade_instruction(running_versions)
                    break

    @classmethod
    def _print_upgrade_instruction(cls, versions: VersionInfo) -> None:
        """Print instructions for how to upgrade Python and the app.

        Print instructions for how to upgrade Python and the application
        to a newer version. This method is called internally by the
        `check_if_unsupported_python` method to print instructions for
        how to upgrade Python and the application to a newer version.

        Args:
            versions: Version information to print.

        """
        pip = 'pip3'
        application_package = list(versions.keys())[0].replace('_', '-')
        if sys.platform.lower().startswith('win') \
                or sys.platform.lower().startswith('nt'):
            pip = 'pip'
        txt = '\nYou are running an old Python version.\n'
        txt += 'Upgrade Python to a new version.\n'
        txt += '(Download Python from https://www.python.org/downloads/ )\n'
        txt += 'After installing new Python, upgrade application with\n'
        txt += pip + f' install --upgrade {cls.get_main_package_name()}\n'
        if application_package != cls.get_main_package_name():
            txt += pip + ' install --upgrade ' + application_package + '\n'
        txt += '\n'
        print(txt)

    @staticmethod
    def _python_version() -> Version:
        """Get the running Python version."""
        py_ver = '.'.join([str(s) for s in sys.version_info[0:3]])
        return Version(py_ver)

    def _get(self) -> VersionInfo:
        """Get version information for the configured packages and Python.

        The returned mapping contains one entry for each package named by
        `package_names()` and an additional `Python` entry for the running
        interpreter version.
        """
        if self.versions is not None:
            return self.versions
        versions: VersionInfo = {i: Version(metadata_version(i))
                                 for i in self.package_names()}
        versions['Python'] = self._python_version()
        self.versions = versions
        return versions

    def package_names(self) -> list[str]:
        """Get the list of packages to get versions for.

        Derived classes must override this method to specify what are
        the names of the packages to get versions for in their context
        (usually in their application). The default value is
        ['versionreporter', 'packaging', 'pypi-simple'],
        which is OK for testing this package, but does not make sense for a
        real application.

        Returns:
            list[str]: List of package names.
        """
        return ['versionreporter', 'packaging', 'pypi-simple']

    def get_app_support_expires(self) -> SupportExpires:
        """Get the Python-version support cutoffs for the application.

        Derived classes should override this method to return a mapping from
        support-end dates to the highest Python major.minor version that
        becomes unsupported on that date. When today's date is on or after
        a listed date, the application treats Python versions up to and
        including the mapped version as unsupported.

        Returns:
        dict[date, str]: Mapping from support-end dates to the highest
                         unsupported Python major.minor version.
        """
        support_end = {date(year=2025, month=10, day=1): '3.10',
                       date(year=2025, month=12, day=1): '3.11',
                       date(year=2026, month=3, day=1): '3.12'}
        return support_end

    def _today(self) -> date:
        """Get today's date."""
        # Mockable to enable easy testing.
        return date.today()

    @staticmethod
    def _get_available_version(pkgname: str, pkgversion: Version,
                               python_version: Version) -> _AvailableVersion:
        """Get information on available versions in PyPI.

        Get information on available versions in PyPI. This method is called
        internally by the `_get_available_versions` method to get information
        on available versions of a package in PyPI.

        Args:
            pkgname: Name of the package to get information on.
            pkgversion: Currently used version of the package. This is used to
                        check if a newer version is available compared to the
                        currently used version.
            python_version: Python version currently used by the application.

        Returns:
            _AvailableVersion: Information on available versions of a package.
        """
        bestver = Version('0.0.1')
        betterver = Version('0.0.1')
        with PyPISimple() as client:
            try:
                page = client.get_project_page(pkgname, timeout=15.0)
            except (NoSuchProjectError, UnsupportedContentTypeError,
                    UnsupportedRepoVersionError, HTTPError):
                return _AvailableVersion(False, False, betterver, betterver,
                                         pkgname=pkgname)
            for pkg in page.packages:
                if pkg.is_yanked:
                    continue
                ver = Version(pkg.version if pkg.version is not None
                              else '0.0.1')
                bestver = max(bestver, ver)
                if ver > betterver:
                    if pkg.requires_python is not None:
                        req = Requirement('python ' + pkg.requires_python)
                        if req.specifier.contains(python_version):
                            betterver = ver
                    else:
                        betterver = ver
        better_for_pyver = betterver > pkgversion
        better_for_new_py = bestver > pkgversion and bestver > betterver
        return _AvailableVersion(is_better_for_pyver=better_for_pyver,
                                 is_best_for_new_py=better_for_new_py,
                                 best_ver=bestver, better_ver=betterver,
                                 pkgname=pkgname)

    @staticmethod
    def _get_available_versions(versions: VersionInfo) -> _AvailableVersions:
        """Get information on available versions in PyPI.

        Get information on available versions in PyPI. This method is called
        internally by the `_print_info_on_new_pkgs` method to get information
        on available versions of the packages in PyPI.

        Args:
            versions: Version information about currently installed versions
                      of the packages.

        Returns:
            _AvailableVersions: List of information on available versions
                                of the packages.
        """
        # pylint: disable=protected-access
        py_ver = versions['Python'] if 'Python' in versions else \
            VersionReporter()._get()['Python']  # pylint: disable=protected-access # noqa: E501
        ret: _AvailableVersions = []
        for pkgname, pkgversion in versions.items():
            if pkgname == 'Python':
                continue
            avail: _AvailableVersion = \
                VersionReporter._get_available_version(pkgname=pkgname,
                                                       pkgversion=pkgversion,
                                                       python_version=py_ver)
            ret.append(avail)
        return ret

    @staticmethod
    def _print_if_better_versions(vers: _AvailableVersions) -> None:
        """Print information if better versions are available.

        Print information if better versions are available. This method is
        called internally by the `_print_info_on_new_pkgs` method to print
        information if better versions are available of packages used by this
        application.

        Args:
            vers: List of information on available versions of the packages
                  used by the application.
        """
        better_for_this: _AvailableVersions = []
        better_with_new_py: _AvailableVersions = []
        for item in vers:
            if item.is_better_for_pyver:
                better_for_this.append(item)
            if item.is_best_for_new_py and item.better_ver != item.best_ver:
                better_with_new_py.append(item)
        if not (better_for_this or better_with_new_py):
            return
        maxlen: int = max(list(len(x.pkgname)
                               for x in better_for_this + better_with_new_py))
        if better_for_this:
            print('Upgraded packages are available for this Python version:')
            for item in better_for_this:
                pad = '.'*(maxlen - len(item.pkgname))
                print(f'{item.pkgname} {pad} {str(item.better_ver)}')
        if better_with_new_py:
            print('Even newer packages are available if upgrading Python:')
            for item in better_with_new_py:
                pad = '.'*(maxlen - len(item.pkgname))
                print(f'{item.pkgname} {pad} {str(item.best_ver)}')

    def _print_info_on_new_pkgs(self,
                                versions: Optional[VersionInfo]
                                = None) -> None:
        """Print information if better versions are available.

        Check if better versions are available of packages used by this
        application and then print information about the available better
        versions.

        Args:
            versions: Optional version information about installed packages.
                      If None, the version information is obtained from the
                      `_get` method.
        """
        if versions is None:
            if self.versions is None:
                self.versions = self._get()
            versions = self.versions
        self._print_if_better_versions(self._get_available_versions(versions))

    @classmethod
    def get_main_package_name(cls) -> str:
        """Get the name of the main package.

        Derived classes should override this method to specify what is
        the name of the main package in their context (usually in their
        application). The default value is 'versionreporter', which is
        OK for testing this package, but does not make sense for a real
        application.

        Returns:
            str: Name of the main package (the PyPI project name).
        """
        return 'versionreporter'

    @classmethod
    def get_recommended_python_version(cls) -> Version:
        """Get recommended Python version.

        Derived classes should override this method to specify what is
        the recommended Python version for the application. The default
        value is Version('3.13'), which is OK for testing this package,
        but may not make sense for the real application.

        Returns:
            Version: Recommended Python version.
        """
        return Version('3.13')
