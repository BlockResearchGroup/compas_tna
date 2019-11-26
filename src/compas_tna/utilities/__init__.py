"""
********************************************************************************
compas_tna.utilities
********************************************************************************

.. currentmodule:: compas_tna.utilities


Functions
=========

.. autosummary::
    :toctree: generated/
    :nosignatures:

    parallelise
    parallelise_sparse
    parallelise_nodal
    rot90
    apply_bounds
    update_z
    update_q_from_qind
    distribute_thickness
    relax_boundary_openings


Proxies
-------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    relax_boundary_openings_proxy


"""
from __future__ import absolute_import

import compas

from .loads import *
from .pattern import *
from .thickness import *

if not compas.IPY:
    from .diagrams import *

__all__ = [name for name in dir() if not name.startswith('_')]
