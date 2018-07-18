from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import random

import compas
import compas_ags
import compas_tna

from compas.utilities import XFunc

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.equilibrium import vertical_from_qind_rhino as vertical_from_qind

from compas_tna.rhino import FormArtist


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


f = XFunc('compas_ags.ags.graphstatics.identify_dof_xfunc')


def identify_dof(form):
    return f(form.to_data())


form = FormDiagram.from_obj(compas.get('lines.obj'))


form.set_vertices_attributes(('is_fixed', 'is_anchor'), (True, True), keys=form.vertices_on_boundary())
form.set_edges_attribute('is_edge', False, keys=form.edges_on_boundary())


k, m, ind = identify_dof(form)

for u, v in ind:
    form.set_edge_attributes((u, v), ('is_ind', 'q'), (True, random.choice(range(1, 5))))

vertical_from_qind(form)


artist = FormArtist(form, layer='FormDiagram')
artist.clear_layer()

artist.draw_vertices(
    color={key: '#ff0000' for key in form.vertices_where({'is_anchor': True})})

artist.draw_edges(
    keys=list(form.edges_where({'is_edge': True})),
    color={(u, v): '#00ff00' for u, v in form.edges_where({'is_ind': True})})

artist.draw_edgelabels(
    text={(u, v): index for index, (u, v, attr) in enumerate(form.edges_where({'is_edge': True}, True)) if attr['is_ind']})

artist.draw_faces()
artist.draw_forces(scale=0.01)
artist.draw_reactions(scale=0.1)
artist.redraw()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
