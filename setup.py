#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='qdpy',
    version='0.1.0-alpha',
    description='A fast distributed Python runtime',
    author='Jeremy Lucas',
    author_email='jeremyalucas@gmail.com',
    url='https://github.com/jerluc/qdpy',
    packages=['qdpy'],
    install_requires=[l.strip() for l in open('requirements.txt')],
    license='License :: OSI Approved :: Apache Software License',
)
