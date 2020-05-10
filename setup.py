#!/usr/bin/env python3
from setuptools import setup
from setuptools.command.test import test

class PyTest(test):

    def run_tests(self):
        import pytest
        pytest.main(self.test_args)

setup(
    name='picmd',
    version='0.4.0',
    packages=['picmd'],
    package_data={
        'picmd': ['py.typed'],
    },
    test_suite='tests',
    python_requires='>=3.7',
    install_requires=[
        'pyserial>=3.4'
    ],
    tests_require=[
        'pytest'
    ],
    cmdclass={'test': PyTest}
)
