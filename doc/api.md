# Table of Contents

* [versionreporter.versionreporter](#versionreporter.versionreporter)
  * [VersionReporter](#versionreporter.versionreporter.VersionReporter)
    * [\_\_init\_\_](#versionreporter.versionreporter.VersionReporter.__init__)
    * [print](#versionreporter.versionreporter.VersionReporter.print)
    * [check\_if\_unsupported\_python](#versionreporter.versionreporter.VersionReporter.check_if_unsupported_python)
    * [package\_names](#versionreporter.versionreporter.VersionReporter.package_names)
    * [get\_app\_support\_expires](#versionreporter.versionreporter.VersionReporter.get_app_support_expires)
    * [get\_main\_package\_name](#versionreporter.versionreporter.VersionReporter.get_main_package_name)
    * [get\_recommended\_python\_version](#versionreporter.versionreporter.VersionReporter.get_recommended_python_version)

<a id="versionreporter.versionreporter"></a>

# versionreporter.versionreporter

Get and print version information.

<a id="versionreporter.versionreporter.VersionReporter"></a>

## VersionReporter Objects

```python
class VersionReporter()
```

Get and print version information.

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

<a id="versionreporter.versionreporter.VersionReporter.__init__"></a>

#### \_\_init\_\_

```python
def __init__() -> None
```

Create a version reporter object.

<a id="versionreporter.versionreporter.VersionReporter.print"></a>

#### print

```python
def print(versions: Optional[VersionInfo] = None) -> None
```

Print version information.

Print version information for the application and the most important
packages that the application uses. The most common usage of this
method is to call it when a `--version` flag is entered on the
command line of the application.

The version information is printed in a table format with the
package names and their versions. If there are newer versions
available for the current Python version, information about these
is also printed. If there are newer versions available for a newer
Python version, information about these is also printed.

**Arguments**:

- `versions` - Optional version information to print. If None,
  the version information is obtained from the
  `_get` method.

<a id="versionreporter.versionreporter.VersionReporter.check_if_unsupported_python"></a>

#### check\_if\_unsupported\_python

```python
def check_if_unsupported_python() -> None
```

Check if the Python version is no longer supported by the app.

This method checks if the running Python version is no longer supported
by the application and prints an appropriate message to the user.
The most common usage of this method is to call it early in the
application program flow.

<a id="versionreporter.versionreporter.VersionReporter.package_names"></a>

#### package\_names

```python
def package_names() -> list[str]
```

Get the list of packages to get versions for.

Derived classes must override this method to specify what are
the names of the packages to get versions for in their context
(usually in their application). The default value is
['versionreporter', 'packaging', 'pypi-simple'],
which is OK for testing this package, but does not make sense for a
real application.

**Returns**:

- `list[str]` - List of package names.

<a id="versionreporter.versionreporter.VersionReporter.get_app_support_expires"></a>

#### get\_app\_support\_expires

```python
def get_app_support_expires() -> SupportExpires
```

Get the Python-version support cutoffs for the application.

Derived classes should override this method to return a mapping from
support-end dates to the highest Python major.minor version that
becomes unsupported on that date. When today's date is on or after
a listed date, the application treats Python versions up to and
including the mapped version as unsupported.

**Returns**:

  dict[date, str]: Mapping from support-end dates to the highest
  unsupported Python major.minor version.

<a id="versionreporter.versionreporter.VersionReporter.get_main_package_name"></a>

#### get\_main\_package\_name

```python
@classmethod
def get_main_package_name(cls) -> str
```

Get the name of the main package.

Derived classes should override this method to specify what is
the name of the main package in their context (usually in their
application). The default value is 'versionreporter', which is
OK for testing this package, but does not make sense for a real
application.

**Returns**:

- `str` - Name of the main package (the PyPI project name).

<a id="versionreporter.versionreporter.VersionReporter.get_recommended_python_version"></a>

#### get\_recommended\_python\_version

```python
@classmethod
def get_recommended_python_version(cls) -> Version
```

Get recommended Python version.

Derived classes should override this method to specify what is
the recommended Python version for the application. The default
value is Version('3.13'), which is OK for testing this package,
but may not make sense for the real application.

**Returns**:

- `Version` - Recommended Python version.

