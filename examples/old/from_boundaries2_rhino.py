from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino
import compas_tna

from compas.utilities import flatten
from compas.utilities import XFunc

from compas.topology import delaunay_from_points
from compas.topology import mesh_flip_cycles
from compas.topology import mesh_unify_cycles
from compas.topology import trimesh_remesh
from compas.geometry import mesh_smooth_area

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.equilibrium import horizontal_rhino as horizontal
from compas_tna.equilibrium import vertical_from_zmax_rhino as vertical_from_zmax
from compas_tna.equilibrium import vertical_from_formforce_rhino as vertical_from_formforce

from compas_tna.rhino import FormArtist

import rhinoscriptsyntax as rs


__author__    = ['Tom Van Mele', 'Matthias Rippmann']
__copyright__ = 'Copyright 2017, BRG - ETH Zurich',
__license__   = 'MIT'
__email__     = 'van.mele@arch.ethz.ch'


# ==============================================================================
# select the input

#guid = compas_rhino.select_polyline("Select boundary.")
#boundary = compas_rhino.get_polyline_coordinates(guid)
#
#guids = compas_rhino.select_polylines("Select holes.")
#holes = [compas_rhino.get_polyline_coordinates(guid) for guid in guids]
#
#points = boundary + list(flatten(holes))

boundary = rs.GetObject("Select Boundary Curve", 4)
length   = rs.GetReal("Select Edge Target Length", 2.0)
points   = rs.DivideCurve(boundary, rs.CurveLength(boundary) / length)

# ==============================================================================
# make a delaunay triangulation
# within the boundary
# and around the holes

faces = delaunay_from_points(points, boundary=points)
faces[:] = [face for face in faces if len(face) > 2]

form = FormDiagram.from_vertices_and_faces(points, faces)

mesh_flip_cycles(form)

trimesh_remesh(form, length, allow_boundary_split=True, allow_boundary_swap=True)

form.edgedata = {}

# ==============================================================================
# update the boundary conditions

boundaries = form.vertices_on_boundaries()

exterior = boundaries[0]
interior = boundaries[1:]

form.set_vertices_attribute('is_anchor', True, keys=exterior)

form.update_exterior(exterior, feet=1)
form.update_interior(interior)

# ==============================================================================
# create the force diagram

force = ForceDiagram.from_formdiagram(form)

# ==============================================================================
# compute equilibrium

horizontal(form, force)

force.attributes['scale'] = 60

# vertical_from_zmax(form, force, zmax=4, kmax=100)
vertical_from_formforce(form, force)

print(max(form.get_vertices_attribute('rx')))

# ==============================================================================
# visualise the result

artist = FormArtist(form, layer="FormDiagram")
artist.clear_layer()

artist.draw_vertices(keys=list(form.vertices_where({'is_external': False})))
artist.draw_edges(keys=list(form.edges_where({'is_edge': True, 'is_external': False})))
artist.draw_faces(fkeys=list(form.faces_where({'is_loaded': True})))
artist.draw_reactions(scale=0.01)
artist.draw_forces(scale=0.01)

artist.redraw()

