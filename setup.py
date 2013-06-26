#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""

    pygenapi

    by hgschmidt

    Copyright (c) 2012 apitrary

"""
from genapi import config

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
    name=config.APP_DETAILS['name'],
    version=config.APP_DETAILS['version'],
    description='Python Generated API for apitrary',
    long_description='pygenapi is apitrary\'s generated REST API project',
    author='Hans-Gunther Schmidt',
    author_email='hgs@apitrary.com',
    maintainer=config.APP_DETAILS['company'],
    maintainer_email=config.APP_DETAILS['support'],
    url='https://github.com/apitrary/pygenapi',
    packages=find_packages('genapi'),
    package_dir={'': 'genapi'},
    scripts=[
        'genapi/genapi_runner.py'
    ],
    license=config.APP_DETAILS['copyright'],
    install_requires=read_requirements()
)
