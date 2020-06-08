#!/usr/bin/env python3
from setuptools import setup
from setuptools.command.test import test

class PyTest(test):

    def run_tests(self):
        import pytest
        pytest.main(self.test_args)

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='picmd',
    version='0.7.0',
    author='ushiboy',
    license='MIT',
    description='Serial Communication Framework for Raspberry PI',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ushiboy/picmd',
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
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux'
    ],
    cmdclass={'test': PyTest}
)
