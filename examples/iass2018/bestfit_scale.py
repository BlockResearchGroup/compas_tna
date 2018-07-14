from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino
import compas_tna

from compas_rhino.helpers import mesh_from_guid

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.equilibrium import horizontal_rhino as horizontal
from compas_tna.equilibrium import vertical_from_target_rhino as vertical_from_target

from compas_tna.rhino import FormArtist


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


# ==============================================================================
# make a form diagram

guid = compas_rhino.select_mesh()
form = mesh_from_guid(FormDiagram, guid)

# ==============================================================================
# update boundary conditions

form.set_vertices_attribute(keys=form.vertices_on_boundary())
