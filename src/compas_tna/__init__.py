"""
********************************************************************************
compas_tna
********************************************************************************

.. currentmodule:: compas_tna


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


__author__ = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2017 - Block Research Group, ETH Zurich'
__license__ = 'MIT License'
__email__ = 'vanmelet@ethz.ch'

__version__ = '0.1.2'


PY3 = sys.version_info.major == 3

HERE = os.path.dirname(__file__)

HOME = os.path.abspath(os.path.join(HERE, '../../'))
DATA = os.path.abspath(os.path.join(HOME, 'data'))
DOCS = os.path.abspath(os.path.join(HOME, 'docs'))
TEMP = os.path.abspath(os.path.join(HOME, 'temp'))


def get(filename):
    """Get the full path to one of the sample data files.

    Parameters
    ----------
    filename : str
        The name of the data file.

    Returns
    -------
    str
        The full path to the specified file.

    Notes
    -----
    The file name should be specified relative to the ``compas_tna`` sample data folder.
    This folder is only locally available if you installed ``compas_tna`` from source,
    or if you are working directly with the source.

    In all other cases, the function will get the corresponding files direcly from
    the GitHub repo, at https://raw.githubusercontent.com/BlockResearchGroup/compas_tna/master/data.

    Examples
    --------
    The ``compas_tna.get`` function is meant to be used in combination with the static
    constructors of the data structures.

    >>> import compas_tna
    >>> from compas_tna.diagrams import FormDiagram
    >>> form = FormDiagram.from_obj(compas.get('faces.obj'))

    """
    filename = filename.strip('/')

    localpath = os.path.abspath(os.path.join(DATA, filename))

    if os.path.exists(localpath):
        return localpath
    else:
        return "https://raw.githubusercontent.com/BlockResearchGroup/compas_tna/master/data/{}".format(filename)
