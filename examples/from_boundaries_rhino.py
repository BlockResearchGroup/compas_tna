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

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.rhino import FormArtist


__author__    = ['Tom Van Mele', 'Matthias Rippmann']
__copyright__ = 'Copyright 2017, BRG - ETH Zurich',
__license__   = 'MIT'
__email__     = 'van.mele@arch.ethz.ch'

__all__ = []


# uses docs/_examples/mesh-delaunay.3dm


def horizontal(form, force, *args, **kwargs):
    def callback(line, args):
        print(line)
        compas_rhino.wait()

    f = XFunc('compas_tna.equilibrium.horizontal_xfunc', callback=callback)
    formdata, forcedata = f(form.to_data(), force.to_data(), *args, **kwargs)
    form.data = formdata
    force.data = forcedata


def vertical_from_zmax(form, force, *args, **kwargs):
    def callback(line, args):
        print(line)
        compas_rhino.wait()

    f = XFunc('compas_tna.equilibrium.vertical_from_zmax_xfunc', callback=callback)
    formdata, forcedata = f(form.to_data(), force.to_data(), *args, **kwargs)
    form.data = formdata
    force.data = forcedata


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

mesh_flip_cycles(form)

# process mesh into form diagram

boundaries = form.vertices_on_boundary()

exterior = boundaries[0]
interior = boundaries[1:]

# anchor the vertices of the exterior boundary

form.set_vertices_attribute('is_anchor', True, keys=exterior)

# update the boundary conditions

form.update_exterior(exterior, feet=2)
form.update_interior(interior)

# relax the interior

# fixed = set(list(flatten(boundaries)) + form.fixed())
# form.relax(fixed=fixed)

# create the force diagram

force = ForceDiagram.from_formdiagram(form)

# compute equilibrium

horizontal(form, force)
vertical_from_zmax(form, force, zmax=40)

# draw the result

artist = FormArtist(form, layer="FormDiagram")
artist.clear_layer()

artist.draw_vertices(keys=list(form.vertices_where({'is_external': False})))
artist.draw_edges(keys=list(form.edges_where({'is_edge': True, 'is_external': False})))
artist.draw_faces(fkeys=list(form.faces_where({'is_loaded': True})), join_faces=True)

artist.draw_reactions(scale=0.01)
artist.draw_forces(scale=0.0001)

artist.redraw()

