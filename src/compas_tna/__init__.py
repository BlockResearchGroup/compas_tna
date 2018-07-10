"""
********************************************************************************
compas_tna
********************************************************************************

.. module:: compas_tna


.. toctree::
    :maxdepth: 1

    compas_tna.diagrams
    compas_tna.equilibrium
    compas_tna.rhino
    compas_tna.utilities

"""
from __future__ import print_function

import os
import sys


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2017 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'
__version__   = '0.1.0'


PY3 = sys.version_info.major == 3

HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, '../../'))
DATA = os.path.abspath(os.path.join(HOME, 'data'))
DOCS = os.path.abspath(os.path.join(HOME, 'docs'))
TEMP = os.path.abspath(os.path.join(HOME, 'temp'))


def get(filename):
    filename = filename.strip('/')
    return os.path.abspath(os.path.join(DATA, filename))
