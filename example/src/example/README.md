# VersionReporter example applications

These example applications are intentionally small enough to read from top to
bottom in one sitting.
They also contain extra teaching comments because they are meant for a
programmer who is new to the `versionreporter` API.

Both examples intentionally use a real PyPI project name as a stand-in for
the application package.
That is necessary because these example scripts are not themselves published
packages, while `VersionReporter` can only report installed package versions
and query PyPI for newer releases of real PyPI project names.

- [`hello_world_minimal.py`](https://bitbucket.org/tom-bjorkholm/version-reporter/src/master/example/src/example/hello_world_minimal.py)
  shows the smallest useful pattern: subclass `VersionReporter`, wire
  `--version` through `argparse`, and print a version report.
- [`hello_world_support_check.py`](https://bitbucket.org/tom-bjorkholm/version-reporter/src/master/example/src/example/hello_world_support_check.py)
  builds on the first example by also calling
  `check_if_unsupported_python()` early in `main()`.
