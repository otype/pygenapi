#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

    pygenapi

    by hgschmidt

    Copyright (c) 2012 apitrary

"""
from setuptools import setup

def read_requirements():
    """
        Read the requirements.txt file
    """
    with open('requirements.txt') as f:
        requirements = f.readlines()
    return [element.strip() for element in requirements]

long_description = ('pygenapi is apitrary\'s generated REST API project')

setup(name='pygenapi',
    version='0.1',
    description='Python Generated API for apitrary',
    long_description=long_description,
    author='Hans-Gunther Schmidt',
    author_email='hgs@apitrar.com',
    maintainer='apitrary',
    maintainer_email='official@apitrary.com',
    url='https://apitrary_hgs@bitbucket.org/apitrary/pygenapi.git',
    packages=['genapi'],
    license='copyright by apitrary',
    install_requires=read_requirements()
)
