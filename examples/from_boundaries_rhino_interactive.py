from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino
import compas_tna

from compas.utilities import flatten
from compas.topology import delaunay_from_points

from compas_tna.rhino import RhinoFormDiagram as FormDiagram
from compas_tna.rhino import RhinoForceDiagram as ForceDiagram

from compas_tna.rhino import FormArtist


# todo: edit attributes of selected vertices
#       mark as anchors, or fixed
#       assign constraints


__author__    = ['Tom Van Mele', 'Matthias Rippmann']
__copyright__ = 'Copyright 2017, BRG - ETH Zurich',
__license__   = 'MIT'
__email__     = 'van.mele@arch.ethz.ch'

__all__ = []


# select the points
# select the boundary
# select the hole(s)

guids = compas_rhino.select_points("Select points.")
points = compas_rhino.get_point_coordinates(guids)

guid = compas_rhino.select_polyline("Select boundary.")
boundary = compas_rhino.get_polyline_coordinates(guid)

guids = compas_rhino.select_polylines("Select holes.")
holes = [compas_rhino.get_polyline_coordinates(guid) for guid in guids]


# make a delaunay triangulation
# within the boundary
# and around the holes

faces = delaunay_from_points(points, boundary=boundary, holes=holes)

form = FormDiagram.from_vertices_and_faces(points, faces)

# process mesh into form diagram

boundaries = form.vertices_on_boundary()

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

# create the force diagram

force = ForceDiagram.from_formdiagram(form)

# draw the result

artist = FormArtist(form, layer="FormDiagram")
artist.clear_layer()
artist.draw_vertices()
artist.draw_edges()
artist.redraw()

