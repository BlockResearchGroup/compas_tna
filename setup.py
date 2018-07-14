#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import print_function

import io
from os import path

from setuptools import find_packages, setup

requirements = []
optional_requirements = {}

here = path.abspath(path.dirname(__file__))

def read(*names, **kwargs):
    return io.open(
        path.join(here, *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()

long_description = read('README.md')

setup(
    name='compas_tna',
    version='0.1.0',
    description='Thrust Network Analysis',
    long_description=long_description,
    license='MIT',
    url='https://github.com/BlockResearchGroup/compas_tna',
    author='Tom Van Mele',
    author_email='van.mele@arch.ethz.ch',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    keywords=['architecture', 'engineering'],
    # TODO: The following excludes don't seem to be really working
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=requirements,
    python_requires='>=2.7',
    extras_require=optional_requirements
    # entry_points={},
)
