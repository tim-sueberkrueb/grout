#!/usr/bin/env python3
# -*- coding: utf-8

import setuptools

setuptools.setup(
    name='baka',
    version='0.1.0',
    description='Baka tool and library for continuous, clean builds',
    license='MIT',
    author='Tim Süberkrüb',
    author_email='dev@timsueberkrueb.io',
    url='https://www.github.com/tim-sueberkrueb',
    packages=setuptools.find_packages(),
    package_data={
        'baka.core': ('validation/project_schema.yaml',)
    },
    scripts=(
        'bin/baka',
    ),
    install_requires=(
        'pylxd',
        'pyyaml',
        'click',
        'pykwalify',
        'pytest'
    ),
    test_suite='tests',
)
