#! /usr/local/bin/python3
"""Setup file specifying build of .whl."""

from setuptools import setup

setup(
  name='versionreporter',
  version='0.4.1',
  description='Report versions on main packages used in program.',
  author='Tom Björkholm',
  author_email='klausuler_linnet0q@icloud.com',
  python_requires='>=3.12',
  packages=['versionreporter'],
  package_dir={'versionreporter': 'src/versionreporter'},
  package_data={'versionreporter': ['py.typed']},
  install_requires=[
    'pypi-simple >= 1.8.0',
    'packaging >= 25.0',
    'requests >= 2.32.5',
    'types-requests >= 2.32.4.20250913',
  ]
)
