# versionreporter

## What is it

The `versionreporter` package provides a very easy way to:

- report the currently used versions of the main packages used in an
  application, including the application package.

- report if there are newer versions available of any of the main packages
  for use on the currently running Python version.

- report if there are newer versions available of any of the main packages
  for use on a newer Python version than the one currently running.

- report when the developer of the main application package will no longer
  provide newer releases for the currently running Python version.

How this is used in an application is naturally up to the application designer.
One common way is to invoke `versionreporter` when a `--version` flag is
entered on the command line of the application.

## Installing versionreporter

### Installing versionreporter on mac and Linux

````sh
pip3 install --upgrade versionreporter
````

### Installing versionreporter on Microsoft Windows

````sh
pip install --upgrade versionreporter
````


## Example programs

The best way to learn to use this package is to use the provided
example programs:
[https://bitbucket.org/tom-bjorkholm/version-reporter/src/master/example/src/example/README.md](https://bitbucket.org/tom-bjorkholm/version-reporter/src/master/example/src/example/README.md).

## API documentation

You can find the public API documentation at [https://bitbucket.org/tom-bjorkholm/version-reporter/src/master/doc/api.md](https://bitbucket.org/tom-bjorkholm/version-reporter/src/master/doc/api.md)

You can find the protected API documentation at [https://bitbucket.org/tom-bjorkholm/version-reporter/src/master/doc/protected_api.md](https://bitbucket.org/tom-bjorkholm/version-reporter/src/master/doc/protected_api.md)

Even though the API documentation exists, most users and programmers probably
get a better start by reading the examples.

## Version history

| Version | Date        | Python version | Comment                     |
|---------|-------------|----------------|-----------------------------|
| 0.1     | 2026 Apr 08 | 3.12 or newer  | First released version      |

## Test summary

- Test result: 197 passed in 7s
- No flake8 warnings.
- No mypy errors found.
- Built version(s): 0.2.1
- Build and test using Python 3.14.3
