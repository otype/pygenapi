#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""

    pygenapi

    by hgschmidt

    Copyright (c) 2012 apitrary

"""
from genapi.genapi_runner import APP_DETAILS

try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    import ez_setup

    ez_setup.use_setuptools()
    from setuptools import setup
    from setuptools import find_packages


def read_requirements():
    """
        Read the requirements.txt file
    """
    with open('requirements.txt') as f:
        requirements = f.readlines()
    return [element.strip() for element in requirements]


setup(
    name=APP_DETAILS['name'],
    version=APP_DETAILS['version'],
    description='Python Generated API for apitrary',
    long_description='pygenapi is apitrary\'s generated REST API project',
    author='Hans-Gunther Schmidt',
    author_email='hgs@apitrary.com',
    maintainer='apitrary',
    maintainer_email='http://apitrary.com/support',
    url='https://github.com/apitrary/pygenapi',
    packages=find_packages('.'),
    package_dir={'': '.'},
    scripts=[
        'genapi/genapi_runner.py'
    ],
    license='(c) 2012 - 2013 apitrary.com',
    install_requires=read_requirements()
)
