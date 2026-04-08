#! /usr/local/bin/python3
"""Test versionreporter package."""

# Copyright (c) 2024-2026 Tom Björkholm
# MIT License


from datetime import date
from copy import deepcopy
from typing import NamedTuple, Optional
from packaging.version import Version
from pypi_simple import ProjectPage, DistributionPackage, \
    NoSuchProjectError
import pytest
from versionreporter import VersionReporter
from versionreporter.versionreporter import VersionInfo, \
    _AvailableVersion, _AvailableVersions


@pytest.mark.parametrize('data, texts',
                         [({'Ab': '1.2.3', 'longer': '4.5', 'short': '6.7.8'},
                           ['Ab .... 1.2.3', 'longer  4.5', 'short . 6.7.8']),
                          ({'really_long': '9.8.7.123', 'another': '1.0'},
                           ['really_long  9.8.7.123', 'another .... 1.0'])
                          ])
@pytest.mark.parametrize('asarg, usearg', [[True, False], [True, False]])
def test_version_print1(capsys: pytest.CaptureFixture[str],
                        data: dict[str, str], texts: list[str],
                        asarg: bool, usearg: bool) -> None:
    """Test VersionReporter.print."""
    class Derived(VersionReporter):
        """Derived class for fake get method."""

        def _get(self) -> VersionInfo:
            """Get fake version info."""
            if asarg:
                return {key: Version(val) for key, val in data.items()}
            return {'Foo': Version('3.1415')}

    vers = Derived()
    versioninfo: VersionInfo = {key: Version(val) for key, val in data.items()}
    vers.print(versioninfo if usearg else None)
    out, err = capsys.readouterr()
    assert err == ''
    if not usearg and not asarg:
        assert out == 'Foo  3.1415\n'
    else:
        for i in texts:
            assert i in out
        rows = out.split('\n')
        for row in rows:
            print(row)
            words = row.split()
            if len(words) > 1:
                assert data[words[0]] == words[-1]


@pytest.mark.parametrize('calls', [0, 1, 2, 8])
def test_version_print2(capsys: pytest.CaptureFixture[str],
                        calls: int) -> None:
    """Test VersionReporter.print loops."""
    num = 0

    class Derived(VersionReporter):
        """Derived class for fake get method."""

        def _get(self) -> VersionInfo:
            """Get fake version info."""
            nonlocal num
            num += 1
            return {'Foo': Version('3.1415')}

    vers = Derived()
    for _ in range(calls):
        vers.print()
    out, err = capsys.readouterr()
    assert err == ''
    assert out == 'Foo  3.1415\n'*calls
    assert num == min(calls, 1)


@pytest.mark.parametrize('vers', [['1', '2.3', '4.5.6', '7b'],
                                  ['4.5', '2.7', '4.5', '1.9.0']])
@pytest.mark.parametrize('pyt', [[3, 10, 7], [3, 13, 1]])
def test_version_get1(monkeypatch: pytest.MonkeyPatch,
                      capsys: pytest.CaptureFixture[str],
                      vers: list[str], pyt: list[int]) -> None:
    """Test VersionReporter.get with patched getters."""
    metaversnum = 0

    def metavers(modulename: str) -> str:
        """Patched metadata.version."""
        assert modulename is not None
        nonlocal metaversnum
        ret = vers[metaversnum]
        metaversnum += 1
        return ret

    mod = 'versionreporter.versionreporter.'
    monkeypatch.setattr(mod + 'sys.version_info', pyt)
    monkeypatch.setattr(mod + 'metadata_version', metavers)
    versionobj = VersionReporter()
    ret = versionobj._get()  # pylint: disable=protected-access
    mods = versionobj.module_names()
    out, err = capsys.readouterr()
    assert '' == err
    assert '' == out
    for i, mod in enumerate(mods):
        assert Version(vers[i]) == ret[mod]


@pytest.mark.parametrize('numcalls', [0, 1, 2, 17])
def test_version_get2(monkeypatch: pytest.MonkeyPatch,
                      capsys: pytest.CaptureFixture[str],
                      numcalls: int) -> None:
    """Test VersionReporter.get with patched getters."""
    calls = 0

    def metavers(modulename: str) -> str:
        """Patched metadata.version."""
        assert modulename is not None
        nonlocal calls
        calls += 1
        return '1.8.2'

    mod = 'versionreporter.versionreporter.'
    monkeypatch.setattr(mod + 'metadata_version', metavers)
    versionobj = VersionReporter()
    for _ in range(numcalls):
        ret = versionobj._get()  # pylint: disable=protected-access
        mods = versionobj.module_names()
        for mod in mods:
            assert ret[mod] == Version('1.8.2')
        # pylint: disable=protected-access
        assert VersionReporter._python_version() == ret['Python']
        assert len(mods) == calls
    if 0 == numcalls:
        assert 0 == calls
    out, err = capsys.readouterr()
    assert '' == err
    assert '' == out


@pytest.mark.parametrize('operatingsys, pip',
                         [('Windows', 'pip'),
                          ('windows', 'pip'),
                          ('linux', 'pip3'),
                          ('darwin', 'pip3')])
def test_print_upgrade(capsys: pytest.CaptureFixture[str],
                       monkeypatch: pytest.MonkeyPatch,
                       operatingsys: str, pip: str) -> None:
    """Test _print_upgrade_instructions."""
    mod = 'versionreporter.versionreporter.sys.platform'
    monkeypatch.setattr(mod, operatingsys)
    versioninfo: VersionInfo = {'aha': Version('0.1')}
    VersionReporter()._print_upgrade_instruction(versioninfo)  # pylint: disable=protected-access # noqa: E501
    out, err = capsys.readouterr()
    assert '' == err
    assert pip + ' install --upgrade aha' in out
    assert pip + ' install --upgrade versionreporter' in out


def test_version_print_old_p(capsys: pytest.CaptureFixture[str],
                             monkeypatch: pytest.MonkeyPatch) -> None:
    """Test version print with old Python."""
    mod = 'versionreporter.versionreporter.sys.version_info'
    monkeypatch.setattr(mod, (3, 11, 1, 0, 0))
    VersionReporter().print()
    out, err = capsys.readouterr()
    assert '' == err
    assert 'versionreporter  0.0.1' in out
    assert 'Python ......... 3.11.1' in out
    assert 'You are running an old Python version.' in out
    assert 'Upgrade Python to a new version.' in out
    assert '(Download Python from https://www.python.org/downloads/ )' in out
    assert 'After installing new Python, upgrade application with' in out
    assert ' install --upgrade ' in out


@pytest.mark.parametrize('ver, dat, errprint',
                         [((3, 11, 1, 0, 0),
                           date(year=2025, month=12, day=25), True),
                          ((3, 11, 1, 0, 0),
                           date(year=2025, month=9, day=25), False),
                          ((3, 11, 1, 0, 0),
                           date(year=2024, month=12, day=25), False),
                          ((3, 10, 11, 75, 0),
                           date(year=2027, month=12, day=25), True)])
def test_version_check_if_u(capsys: pytest.CaptureFixture[str],
                            monkeypatch: pytest.MonkeyPatch,
                            ver: tuple[int, int, int, int, int],
                            dat: date, errprint: bool) -> None:
    """Test version check if unsupported python widh old Python."""
    mod = 'versionreporter.versionreporter.sys.version_info'
    monkeypatch.setattr(mod, ver)

    class MockVersion1(VersionReporter):
        """Version with mocked today."""

        def _today(self) -> date:
            """Mock today."""
            return dat

    MockVersion1().check_if_unsupported_python()
    out, err = capsys.readouterr()
    assert '' == err
    if errprint:
        assert 'You are running an old version of Python:' in out
        assert 'This application no longer releases bug fixes ' in out
        assert 'for this old Python version.' in out
        assert 'Upgrade Python to a new version.' in out
        assert '(Download Python from https://www.python.org/downloads' in out
        assert 'After installing new Python, upgrade application with' in out
        assert ' install --upgrade ' in out
    else:
        assert '' == out


@pytest.mark.parametrize('ver, res',
                         [((3, 11, 2, 0, 0), '3.11.2'),
                          ((3, 13, 3, 0, 0), '3.13.3'),
                          ((3, 14, 4, 0, 0), '3.14.4'),
                          ((3, 10, 5, 0, 0), '3.10.5')])
def test_python_version(capsys: pytest.CaptureFixture[str],
                        monkeypatch: pytest.MonkeyPatch,
                        ver: tuple[int, int, int, int, int],
                        res: str) -> None:
    """Test VersionsInformation.python_version."""
    mod = 'versionreporter.versionreporter.sys.version_info'
    monkeypatch.setattr(mod, ver)
    ret = VersionReporter._python_version()  # pylint: disable=protected-access
    out, err = capsys.readouterr()
    assert Version(res) == ret
    assert res == str(ret)
    assert '' == out
    assert '' == err


class MockReturn(NamedTuple):
    """What should packages in mocked page be like."""

    version: str
    is_yanked: bool
    req_python: Optional[str]


type PageReturn = list[MockReturn]
type PageReturns = list[PageReturn]

pagereturns: PageReturns = []


def mocked_get_project_page(_: object, project: str,
                            timeout: float | tuple[float, float] | None
                            = None, accept: Optional[str] = None,
                            headers: Optional[dict[str, str]]
                            = None) -> ProjectPage:
    """Mock PyPISimple.get_project_page."""
    packages: list[DistributionPackage] = []
    assert timeout is not None
    assert accept is None
    assert headers is None
    if not pagereturns or pagereturns[-1] is None:
        raise NoSuchProjectError(project=project, url='')
    mockvals: PageReturn = pagereturns.pop()
    for mockret in mockvals:
        packages.append(DistributionPackage(filename=f'{project}.whl',
                                            url='',
                                            project=project,
                                            package_type='wheel',
                                            version=mockret.version,
                                            digests={},
                                            requires_python=mockret.req_python,
                                            has_sig=False,
                                            is_yanked=mockret.is_yanked))
    return ProjectPage(project=project, packages=packages,
                       repository_version=None, last_serial=None)


@pytest.mark.parametrize('page,name,ver,pyver,res',
                         [([MockReturn(version='1.0', is_yanked=False,
                                       req_python=''),
                            MockReturn(version='10.1', is_yanked=False,
                                       req_python='>= 3.0')],
                           'abc', '2.0', '3.10',
                           _AvailableVersion(is_better_for_pyver=True,
                                             is_best_for_new_py=False,
                                             best_ver=Version('10.1'),
                                             better_ver=Version('10.1'),
                                             pkgname='abc')),
                          ([MockReturn(version='3.0', is_yanked=False,
                                       req_python=''),
                            MockReturn(version='10.1', is_yanked=False,
                                       req_python='>= 3.12')],
                           'ghi', '2.0', '3.10',
                           _AvailableVersion(is_better_for_pyver=True,
                                             is_best_for_new_py=True,
                                             best_ver=Version('10.1'),
                                             better_ver=Version('3.0'),
                                             pkgname='ghi')),
                          ([MockReturn(version='3.0', is_yanked=False,
                                       req_python=''),
                            MockReturn(version='10.1', is_yanked=True,
                                       req_python='>= 3.12')],
                           'jkl', '2.0', '3.10',
                           _AvailableVersion(is_better_for_pyver=True,
                                             is_best_for_new_py=False,
                                             best_ver=Version('3.0'),
                                             better_ver=Version('3.0'),
                                             pkgname='jkl')),
                          ([MockReturn(version='3.0', is_yanked=False,
                                       req_python='>= 3.12'),
                            MockReturn(version='10.1', is_yanked=False,
                                       req_python='>= 3.12')],
                           'mno', '4.0', '3.10',
                           _AvailableVersion(is_better_for_pyver=False,
                                             is_best_for_new_py=True,
                                             best_ver=Version('10.1'),
                                             better_ver=Version('0.0.1'),
                                             pkgname='mno')),
                          ([MockReturn(version='1.0', is_yanked=False,
                                       req_python='>= 3.12'),
                            MockReturn(version='3.1', is_yanked=False,
                                       req_python='>= 3.12')],
                           'pqr', '4.0', '3.10',
                           _AvailableVersion(is_better_for_pyver=False,
                                             is_best_for_new_py=False,
                                             best_ver=Version('3.1'),
                                             better_ver=Version('0.0.1'),
                                             pkgname='pqr')),
                          ([MockReturn(version='3.0', is_yanked=False,
                                       req_python=None),
                            MockReturn(version='11.1', is_yanked=False,
                                       req_python=None)],
                           'stu', '4.0', '3.10',
                           _AvailableVersion(is_better_for_pyver=True,
                                             is_best_for_new_py=False,
                                             best_ver=Version('11.1'),
                                             better_ver=Version('11.1'),
                                             pkgname='stu')),
                          (None, 'def', '2.0', '3.12',
                           _AvailableVersion(is_better_for_pyver=False,
                                             is_best_for_new_py=False,
                                             best_ver=Version('0.0.1'),
                                             better_ver=Version('0.0.1'),
                                             pkgname='def'))])
def test_get_avail_version(capsys: pytest.CaptureFixture[str],  # pylint: disable=too-many-arguments,too-many-positional-arguments) # noqa: E501
                           monkeypatch: pytest.MonkeyPatch,
                           page: list[MockReturn], name: str,
                           ver: str, pyver: str,
                           res: _AvailableVersion) -> None:
    """Test VersionReporter.get_available_version."""
    global pagereturns  # pylint: disable=global-statement
    pagereturns = [page]
    mod = 'versionreporter.versionreporter.PyPISimple.'
    monkeypatch.setattr(mod + 'get_project_page', mocked_get_project_page)
    pkgversion = Version(ver)
    pyversion = Version(pyver)
    # pylint: disable=protected-access
    ret = VersionReporter._get_available_version(pkgname=name,
                                                 pkgversion=pkgversion,
                                                 python_version=pyversion)
    out, err = capsys.readouterr()
    assert res == ret
    assert '' == out
    assert '' == err


def mock_get_available_version(pkgname: str,
                               pkgversion: Version,
                               python_version: Version) -> _AvailableVersion:
    """Get information on available version in PyPi."""
    assert pkgversion is not None
    assert python_version is not None
    for ans in mock_get_available_version_answers:
        if ans.pkgname == pkgname:
            return ans
    return _AvailableVersion(pkgname=pkgname, is_best_for_new_py=False,
                             is_better_for_pyver=False,
                             best_ver=Version('0.0'),
                             better_ver=Version('0.0'))


mock_get_available_version_answers: _AvailableVersions = []


@pytest.mark.parametrize('inp,ans,res',
                         [({'abc': Version('1.0'),
                            'Python': Version('2.1'),
                            'def': Version('1.0')},
                           [_AvailableVersion(pkgname='def',
                                              is_better_for_pyver=True,
                                              is_best_for_new_py=True,
                                              best_ver=Version('10.1'),
                                              better_ver=Version('5.0')),
                            _AvailableVersion(pkgname='abc',
                                              is_better_for_pyver=False,
                                              is_best_for_new_py=False,
                                              best_ver=Version('1.0'),
                                              better_ver=Version('1.0')),
                            _AvailableVersion(pkgname='Python',
                                              is_better_for_pyver=True,
                                              is_best_for_new_py=True,
                                              best_ver=Version('3.14'),
                                              better_ver=Version('3.13'))],
                           [_AvailableVersion(pkgname='abc',
                                              is_better_for_pyver=False,
                                              is_best_for_new_py=False,
                                              best_ver=Version('1.0'),
                                              better_ver=Version('1.0')),
                            _AvailableVersion(pkgname='def',
                                              is_better_for_pyver=True,
                                              is_best_for_new_py=True,
                                              best_ver=Version('10.1'),
                                              better_ver=Version('5.0'))]),
                          ({'def': Version('1.0'),
                            'abc': Version('2.1'),
                            'Python': Version('1.0')},
                           [_AvailableVersion(pkgname='def',
                                              is_better_for_pyver=True,
                                              is_best_for_new_py=True,
                                              best_ver=Version('10.1'),
                                              better_ver=Version('5.0')),
                            _AvailableVersion(pkgname='abc',
                                              is_better_for_pyver=False,
                                              is_best_for_new_py=True,
                                              best_ver=Version('10.0'),
                                              better_ver=Version('1.0')),
                            _AvailableVersion(pkgname='Python',
                                              is_better_for_pyver=True,
                                              is_best_for_new_py=True,
                                              best_ver=Version('3.14'),
                                              better_ver=Version('3.13'))],
                           [_AvailableVersion(pkgname='def',
                                              is_better_for_pyver=True,
                                              is_best_for_new_py=True,
                                              best_ver=Version('10.1'),
                                              better_ver=Version('5.0')),
                            _AvailableVersion(pkgname='abc',
                                              is_better_for_pyver=False,
                                              is_best_for_new_py=True,
                                              best_ver=Version('10.0'),
                                              better_ver=Version('1.0'))])])
def test_get_available_versions(capsys: pytest.CaptureFixture[str],
                                monkeypatch: pytest.MonkeyPatch,
                                inp: dict[str, Version],
                                ans: list[_AvailableVersion],
                                res: _AvailableVersions) -> None:
    """Test VersionReporter.get_available_versions."""
    mod = 'versionreporter.versionreporter.VersionReporter.'
    monkeypatch.setattr(mod + '_get_available_version',
                        mock_get_available_version)
    global mock_get_available_version_answers  # pylint: disable=global-statement # noqa: E501
    mock_get_available_version_answers = deepcopy(ans)
    vers = VersionReporter()
    ret = vers._get_available_versions(inp)  # pylint: disable=protected-access
    out, err = capsys.readouterr()
    assert ret == res
    assert '' == out
    assert '' == err


PBAVAIL1: _AvailableVersions = [
    _AvailableVersion(pkgname='abc', is_best_for_new_py=False,
                      is_better_for_pyver=False,
                      best_ver=Version('1.0'), better_ver=Version('1.0'))
]
PBTXT1 = ''
PBAVAIL2: _AvailableVersions = [
    _AvailableVersion(pkgname='abc', is_best_for_new_py=False,
                      is_better_for_pyver=True,
                      best_ver=Version('2.0'), better_ver=Version('2.0')),
    _AvailableVersion(pkgname='longer_name', is_best_for_new_py=True,
                      is_better_for_pyver=False,
                      best_ver=Version('10.0'), better_ver=Version('1.0'))
]
PBTXT2 = '''Upgraded packages are available for this python version:
abc ........ 2.0
Even newer packages are available if upgrading python:
longer_name  10.0
'''
PBAVAIL3: _AvailableVersions = [
    _AvailableVersion(pkgname='abc', is_best_for_new_py=True,
                      is_better_for_pyver=True,
                      best_ver=Version('2.1'), better_ver=Version('2.0')),
    _AvailableVersion(pkgname='longer_name', is_best_for_new_py=True,
                      is_better_for_pyver=True,
                      best_ver=Version('10.0'), better_ver=Version('1.0'))
]
PBTXT3 = '''Upgraded packages are available for this python version:
abc ........ 2.0
longer_name  1.0
Even newer packages are available if upgrading python:
abc ........ 2.1
longer_name  10.0
'''


@pytest.mark.parametrize('avai,printout',
                         [(PBAVAIL1, PBTXT1),
                          (PBAVAIL2, PBTXT2),
                          (PBAVAIL3, PBTXT3)])
def test_print_if_better_versions(capsys: pytest.CaptureFixture[str],
                                  avai: _AvailableVersions,
                                  printout: str) -> None:
    """Test VersionReporter.print_if_better_versions."""
    vers = VersionReporter()
    vers._print_if_better_versions(avai)  # pylint: disable=protected-access
    out, err = capsys.readouterr()
    assert '' == err
    assert printout == out


def test_print_info_on_new_1(capsys: pytest.CaptureFixture[str],
                             monkeypatch: pytest.MonkeyPatch) -> None:
    """Test normal case of VersionReporter.print_info_on_new_pkgs."""
    get_avail_num = 0
    print_if_better_num = 0

    def mock_get_avail(_: object, versions: VersionInfo) -> _AvailableVersions:
        """Mock VersionReporter.get_available_versions."""
        nonlocal get_avail_num
        get_avail_num += 1
        assert versions is not None
        assert isinstance(versions, dict)
        return [_AvailableVersion(pkgname='versionreporter',
                                  is_best_for_new_py=False,
                                  is_better_for_pyver=False,
                                  best_ver=Version('1.0'),
                                  better_ver=Version('1.0'))]

    def mock_print_if_better(_: object, vers: _AvailableVersions) -> None:
        """Mock VersionReporter.print_if_better_versions."""
        nonlocal print_if_better_num
        print_if_better_num += 1
        assert len(vers) == 1
        assert isinstance(vers[0], _AvailableVersion)
        assert vers[0].pkgname == 'versionreporter'

    mod = 'versionreporter.versionreporter.VersionReporter.'
    monkeypatch.setattr(mod + '_get_available_versions',
                        mock_get_avail)
    monkeypatch.setattr(mod + '_print_if_better_versions',
                        mock_print_if_better)
    vers = VersionReporter()
    vers._print_info_on_new_pkgs()  # pylint: disable=protected-access
    out, err = capsys.readouterr()
    assert get_avail_num == 1
    assert print_if_better_num == 1
    assert '' == err
    assert '' == out


def test_print_info_on_new_2(capsys: pytest.CaptureFixture[str],
                             monkeypatch: pytest.MonkeyPatch) -> None:
    """Test print_info_on_new_pkgs with mocked_get_project_page."""
    global pagereturns  # pylint: disable=global-statement
    pagereturns = [[MockReturn(version='10.1', is_yanked=False,
                               req_python=None),
                    MockReturn(version='10.2', is_yanked=False,
                               req_python=' >=3.17')],
                   [MockReturn(version='11.1', is_yanked=False,
                               req_python=None),
                    MockReturn(version='11.2', is_yanked=False,
                               req_python=' >=3.17')],
                   [MockReturn(version='12.1', is_yanked=False,
                               req_python=None),
                    MockReturn(version='12.2', is_yanked=False,
                               req_python=' >=3.17')],
                   [MockReturn(version='13.1', is_yanked=False,
                               req_python=None),
                    MockReturn(version='13.2', is_yanked=False,
                               req_python=' >=3.17')],
                   [MockReturn(version='14.1', is_yanked=False,
                               req_python=None),
                    MockReturn(version='14.2', is_yanked=False,
                               req_python=' >=3.17')],
                   [MockReturn(version='15.1', is_yanked=False,
                               req_python=None),
                    MockReturn(version='15.2', is_yanked=False,
                               req_python=' >=3.17')]]
    mod = 'versionreporter.versionreporter.PyPISimple.'
    monkeypatch.setattr(mod + 'get_project_page', mocked_get_project_page)
    vers = VersionReporter()
    vers._print_info_on_new_pkgs()  # pylint: disable=protected-access
    out, err = capsys.readouterr()
    assert '' == err
    txt = '''Upgraded packages are available for this python version:
versionreporter  15.1
pypi-simple .... 13.1
Even newer packages are available if upgrading python:
versionreporter  15.2
pypi-simple .... 13.2
'''
    assert txt == out
