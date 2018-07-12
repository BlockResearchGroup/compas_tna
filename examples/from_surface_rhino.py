from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino
import compas_tna

from compas.files import OBJ
from compas.utilities import pairwise

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.equilibrium import horizontal_nodal
from compas_tna.equilibrium import vertical_from_zmax


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


# per patch of the surface, use the uv space to align quadmesh
# merge vertices at the seems
# unanchor (is_anchor: False) all vertices along unsupported openings
# add corresponding faces
# mark relevant edges as nonedges
# use trims for openings
# use curves for features (creases, openings, ...)
