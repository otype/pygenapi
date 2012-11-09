#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""

    pygenapi

    by hgschmidt

    Copyright (c) 2012 apitrary

"""
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

long_description = ('pygenapi is apitrary\'s generated REST API project')

setup(name='pygenapi',
    version='0.3.5',
    description='Python Generated API for apitrary',
    long_description=long_description,
    author='Hans-Gunther Schmidt',
    author_email='hgs@apitrar.com',
    maintainer='apitrary',
    maintainer_email='official@apitrary.com',
    url='https://apitrary_hgs@bitbucket.org/apitrary/pygenapi.git',
    packages=['genapi'],
    package_dir={'': '.'},
    scripts=['genapi/genapi_runner.py'],
    license='copyright by apitrary',
    install_requires=read_requirements()
)
