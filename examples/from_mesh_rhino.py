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

from compas_rhino import MeshArtist


# todo: select a rhino mesh as input


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


def horizontal(form, force, *args, **kwargs):
    def callback(line, args):
        print(line)
        compas_rhino.wait()

    f = XFunc('compas_tna.equilibrium.horizontal_xfunc', callback=callback)
    formdata, forcedata = f(form.to_data(), force.to_data(), *args, **kwargs)
    form.data = formdata
    force.data = forcedata


def horizontal_nodal(form, force, *args, **kwargs):
    def callback(line, args):
        print(line)
        compas_rhino.wait()

    f = XFunc('compas_tna.equilibrium.horizontal_nodal_xfunc', callback=callback)
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


# make a form diagram from an obj file

file = compas_tna.get('mesh.obj')
form = FormDiagram.from_obj(file)

artist = MeshArtist(form, layer='FormDiagram')

# collapse edges that are shorter than 0.5

form.collapse_small_edges(tol=0.5)

artist.clear()
artist.draw_vertices()
artist.draw_edges()
artist.redraw()

# extract the exterior and interior boundaries

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
artist.draw_faces()
artist.redraw()
