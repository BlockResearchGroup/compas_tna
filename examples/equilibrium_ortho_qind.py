from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import random

import compas
import compas_ags
import compas_tna

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_ags.ags import identify_dof

from compas_tna.equilibrium import horizontal
from compas_tna.equilibrium import vertical_from_qind

from compas_tna.viewers import FormViewer


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


# the boundary conditions should be set such that the fore diagram has only closed convex faces
# all internal and external forces (loads and reactions) should eb included in the form diagram
# for a fixed pattern, equilibrium can be computed by controlling the independent edges
# or by a parallellisation procedure involving the force diagram
# in the former case, the force diagram can be constructed from the force densities of the form diagram


form = FormDiagram.from_obj(compas.get('lines.obj'))


form.set_vertices_attributes(('is_fixed', 'is_anchor'), (True, True), keys=form.vertices_on_boundary())
form.set_edges_attribute('is_edge', False, keys=form.edges_on_boundary())


k, m, ind = identify_dof(form)

for u, v in ind:
    form.set_edge_attributes((u, v), ('is_ind', 'q'), (True, random.choice(range(1, 5))))

e = len(list(form.edges_where({'is_edge': True})))
l = sum(form.edge_length(u, v) for u, v in form.edges_where({'is_edge': True})) / e
d = (200) ** 0.5 / e
rho = 0.5 * l * d

# if no convergence after 100 iterations
# increase the scale

# check zmax => 0.1 * d < zmax < 0.5 * d

print(rho)

vertical_from_qind(form, density=d, kmax=200)


viewer = FormViewer(form, figsize=(10, 7))
viewer.defaults['vertex.fontsize'] = 6

viewer.draw_vertices(
    facecolor={key: '#ff0000' for key in form.vertices_where({'is_anchor': True})},
    text={key: "{:.1f}".format(attr['z']) for key, attr in form.vertices_where({'is_anchor': False}, True)},
    radius=0.2)

viewer.draw_edges(
    keys=list(form.edges_where({'is_edge': True})),
    width={key: 3.0 for key in form.edges_where({'is_ind': True})},
    text={(u, v): "{:.1f}".format(attr['q']) for u, v, attr in form.edges_where({'is_edge': True}, True)})

viewer.draw_faces()
viewer.show()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
