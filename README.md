# version-reporter

> **👤 Looking to use this in your program**  
> This repository is for developers of the package. If you want to install
> and use `versionreporter` including writing programs that use them, please visit
> the **PyPI project page [https://pypi.org/project/versionreporter](https://pypi.org/project/versionreporter)
> for installation instructions and user documentation.

## What is it

The `versionreporter` package provides a very easy way to:

- report the currently used versions of the main packages used in an
  application including the application package.

- report if there are newer versions available of any of the main packages
  for use on the currently running Python version.

- report if there are newer versions available of any of the main packages
  for use on a newer Python version than the one currently running.

- report when the developer of the main application package no longer will
  provide newer releases for the currently running Python version.

How this is used in an application is naturally up to the application designer.
One common way is to invoke the versionreporter when a `--version` flag is
entered on the command line of the application.

## For developers

### Cloning

The version-reporter repo uses submodules. To clone it use the command:

````sh
git clone --recurse-submodules git@github.com:tom-bjorkholm/version-reporter.git
````

If you forgot to include the `--recurse-submodules` in your `git clone` command
you can fix it later with the command:

````sh
git submodule update --init --recursive 
````

To update the version of thr submodule repo that you see in the main repo use the command:

````sh
git submodule update --remote --merge
````

### Needed environment

#### OS

For running the script and running the test suite you need a mac or a Linux computer.
Even if the resulting package can be installed and used on Windows, the scripts for
building and testing are only implemented for mac and Linux.

#### Python version

Please see README_pypi.md for information on needed python version.
Main development is on newest Python version.

### Quick start

1. Clone this repository
2. Run `./run_setup_build_environment.py` to set up the build environment
3. Run `./run_build.py`  to build and test the package

### Building application

There are 3 main scripts (and 2 extra convinience scripts) for building the application:

- `run_setup_build_environment.py` Run this script first to get the
  environment set up for building.
- `run_build.py` Run this script to build an installation package (.whl) and
  to run the tests on it in a venv (virtual environment).
- `run_clean.py` Deletes all files that was produced by the build to start
  over from a clean state.
- `run_clean_build.py` Combines the use of `run_clean.py`,
  `run_setup_build_environment.py` and `run_build.py` into one script.
  Pylint discover some duplicate code warnings only on a clean build so this
  is useful.
- `run_pypi_build.py` Builds for PyPI upload and can do the upload too.

The "testing" includes pytest, pylint, flake8 and mypy.

After running `run_build.py` you can open `reports/index.html` to see all test
reports.

### More build system information

The file `./common_build_tools/README.md` (in git submodule - see above) contains more
information about the build system. This README can also be viewed at
[https://github.com/tom-bjorkholm/common_build_tools/blob/master/README.md](https://github.com/tom-bjorkholm/common_build_tools/blob/master/README.md)

## Test summary

- Test result: 255 passed in 5s
- No flake8 warnings.
- No mypy errors found.
- No pylint warnings.
- No python layout warnings.
- Built version(s): 0.5.1
- Build and test using Python 3.15.1
