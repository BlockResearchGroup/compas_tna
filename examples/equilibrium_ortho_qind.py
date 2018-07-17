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

from compas_tna.equilibrium import vertical_from_qind

from compas_tna.viewers import FormViewer


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


def identify_dof(form):
    f = XFunc('compas_ags.ags.graphstatics.identify_dof_xfunc')
    return f(form.to_data())


form = FormDiagram.from_obj(compas.get('lines.obj'))


form.set_vertices_attributes(('is_fixed', 'is_anchor'), (True, True), keys=form.vertices_on_boundary())
form.set_edges_attribute('is_edge', False, keys=form.edges_on_boundary())


k, m, ind = identify_dof(form)

for u, v in ind:
    form.set_edge_attributes((u, v), ('is_ind', 'q'), (True, random.choice(range(1, 10))))

vertical_from_qind(form, density=0.6)


form.to_json(os.path.join(compas_tna.DATA, 'notrhino.json'))


viewer = FormViewer(form, figsize=(10, 7))
viewer.defaults['vertex.fontsize'] = 6

viewer.draw_vertices(
    facecolor={key: '#ff0000' for key in form.vertices_where({'is_anchor': True})},
    text={key: "{:.1f}".format(attr['z']) for key, attr in form.vertices_where({'is_anchor': False}, True)},
    radius=0.2)

viewer.draw_edges(
    keys=list(form.edges_where({'is_edge': True})),
    width={key: 3.0 for key in form.edges_where({'is_ind': True})})

viewer.draw_faces()
viewer.show()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
