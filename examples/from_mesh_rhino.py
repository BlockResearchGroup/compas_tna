from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from math import pi
from math import cos
from math import sin
from math import sqrt

import compas
import compas_rhino
import compas_tna

from compas.utilities import flatten
from compas.utilities import i_to_red
from compas.utilities import XFunc

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.equilibrium import horizontal_rhino as horizontal
from compas_tna.equilibrium import horizontal_nodal_rhino as horizontal_nodal
from compas_tna.equilibrium import vertical_from_zmax_rhino as vertical_from_zmax
from compas_tna.equilibrium import vertical_from_formforce_rhino as vertical_from_formforce

from compas_tna.rhino import FormArtist


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


# make a form diagram from an obj file

file = compas.get('faces.obj')
form = FormDiagram.from_obj(file)

# update the boundary conditions

boundaries = form.vertices_on_boundaries()

exterior = boundaries[0]
interior = boundaries[1:]

form.set_vertices_attribute('is_anchor', True, keys=exterior)

form.update_exterior(exterior, feet=1)
form.update_interior(interior)

# create the force diagram

force = ForceDiagram.from_formdiagram(form)

# compute equilibrium

horizontal(form, force, kmax=20, display=True)
vertical_from_formforce(form, force, density=form.init_scale(), kmax=100)

# visualise result

artist = FormArtist(form, layer='FormDiagram')

artist.clear_layer()

artist.draw_vertices(keys=list(form.vertices_where({'is_external': False})))
artist.draw_edges(keys=list(form.edges_where({'is_edge': True, 'is_external': False})))
artist.draw_faces(fkeys=list(form.faces_where({'is_loaded': True})), join_faces=True)

artist.draw_reactions(scale=1.0)
artist.draw_forces(scale=0.05)

artist.redraw()
