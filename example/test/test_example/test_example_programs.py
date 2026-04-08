#! /usr/local/bin/python3
"""Test the example applications."""

# Copyright (c) 2026 Tom Björkholm
# MIT License


from datetime import date
from typing import Callable, Optional
from pypi_simple import DistributionPackage, ProjectPage
import pytest
from example.hello_world_minimal import main as minimal_main
from example.hello_world_support_check import \
    SupportAwareHelloVersionReporter, main as support_main
from versionreporter import VersionReporter


def _distribution_package(project: str, version: str) -> DistributionPackage:
    """Create one fake package entry returned from the PyPI client."""
    return DistributionPackage(
        filename=f'{project}-{version}.whl',
        url='',
        project=project,
        version=version,
        package_type='wheel',
        digests={},
        requires_python='>= 3.0',
        has_sig=False,
        is_yanked=False
    )


def _mock_get_project_page(
        _: object,
        project: str,
        timeout: Optional[float | tuple[float, float]] = None,
        accept: Optional[str] = None,
        headers: Optional[dict[str, str]] = None) -> ProjectPage:
    """Return a fake project page that always advertises a newer version."""
    assert timeout is not None
    assert accept is None
    assert headers is None
    packages = [_distribution_package(project=project, version='999.0')]
    return ProjectPage(project=project, packages=packages,
                       repository_version=None, last_serial=None)


def _patch_pypi_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the low-level PyPI lookup used by VersionReporter."""
    monkeypatch.setattr(
        'versionreporter.versionreporter.PyPISimple.get_project_page',
        _mock_get_project_page
    )


@pytest.mark.parametrize('main_function, argv, text',
                         [(minimal_main, [], 'Hello, world!'),
                          (support_main, ['--name', 'reader'],
                           'Hello, reader!')])
def test_example_programs_normal_flow(
        capsys: pytest.CaptureFixture[str],
        main_function: Callable[[Optional[list[str]]], int],
        argv: list[str],
        text: str) -> None:
    """Test the normal non-version flow of the example programs."""
    assert 0 == main_function(argv)
    out, err = capsys.readouterr()
    assert '' == err
    assert text in out
    assert 'You are running an old version of Python:' not in out


@pytest.mark.parametrize('main_function, main_package',
                         [(minimal_main, 'build'),
                          (support_main, 'requests')])
def test_example_programs_report_newer_versions(
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
        main_function: Callable[[Optional[list[str]]], int],
        main_package: str) -> None:
    """Test that the examples report newer package versions."""
    _patch_pypi_lookup(monkeypatch)
    assert 0 == main_function(['--version'])
    out, err = capsys.readouterr()
    assert '' == err
    assert main_package in out
    assert 'versionreporter' in out
    assert 'Python' in out
    assert 'Upgraded packages are available for this Python version:' in out
    assert '999.0' in out


def test_support_aware_example_reports_unsupported_python(
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str]) -> None:
    """Test the support-aware example warning for unsupported Python."""
    def mock_today(_: VersionReporter) -> date:
        """Return a date after the support deadline for Python 3.12."""
        return date(year=2027, month=6, day=2)

    monkeypatch.setattr('versionreporter.versionreporter.sys.version_info',
                        (3, 12, 9, 0, 0))
    monkeypatch.setattr(SupportAwareHelloVersionReporter, '_today',
                        mock_today)
    assert 0 == support_main(['--name', 'reader'])
    out, err = capsys.readouterr()
    assert '' == err
    assert 'You are running an old version of Python:' in out
    assert 'Upgrade Python to a new version.' in out
    assert 'Hello, reader!' in out
