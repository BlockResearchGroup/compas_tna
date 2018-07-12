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

from compas_tna.equilibrium import horizontal_nodal_rhino as horizontal_nodal
from compas_tna.equilibrium import vertical_from_zmax_rhino as vertical_from_zmax

from compas_tna.rhino import FormArtist


# todo: select a rhino mesh as input
# todo: use the form artist
# todo: simplify redrawing


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


# make a form diagram from an obj file

file = compas_tna.get('mesh.obj')
form = FormDiagram.from_obj(file)

artist = FormArtist(form, layer='FormDiagram')

# collapse edges that are shorter than 0.5

form.collapse_small_edges(tol=0.5)

artist.clear()
artist.draw_vertices()
artist.draw_edges()
artist.redraw()

# extract the exterior and interior boundaries

boundaries = form.vertices_on_boundaries()

exterior = boundaries[0]
interior = boundaries[1:]

# anchor the vertices of the exterior boundary

form.set_vertices_attribute('is_anchor', True, keys=exterior)

# update the boundary conditions

form.update_exterior(exterior, feet=1)
form.update_interior(interior)

# relax the interior

fixed = set(list(flatten(boundaries)) + form.fixed())

form.relax(fixed=fixed)

artist.clear()
artist.draw_vertices()
artist.draw_edges()
artist.redraw()

# create the force diagram

force = ForceDiagram.from_formdiagram(form)

# compute equilibrium

horizontal_nodal(form, force)
vertical_from_zmax(form, force, zmax=15)

# visualise result

artist.clear()
artist.draw_vertices()
artist.draw_edges()
artist.draw_faces(join_faces=True)
artist.redraw()
