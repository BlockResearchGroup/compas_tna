from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_tna

from compas.topology import mesh_flip_cycles

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.equilibrium import horizontal
from compas_tna.equilibrium import vertical_from_zmax
from compas_tna.equilibrium import vertical_from_target
from compas_tna.equilibrium import vertical_from_self
from compas_tna.equilibrium import vertical_from_formforce

from compas_tna.viewers import FormViewer


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


# ==============================================================================
# make a form diagram from an obj file

form = FormDiagram.from_obj(compas.get('faces.obj'))

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

horizontal(form, force, display=False)

vertical_from_zmax(form, force, zmax=3, tol=1e-5)
vertical_from_self(form, force)
vertical_from_formforce(form, force)

print('scale:', force.attributes['scale'])
print('zmax:', max(form.get_vertices_attribute('z')))
print('residual:', form.residual())

# ==============================================================================
# visualise result

viewer = FormViewer(form, figsize=(10, 7))
viewer.defaults['edge.fontsize'] = 4

viewer.draw_vertices(
    keys=list(form.vertices_where({'is_external': False}))
)
viewer.draw_edges(
    keys=list(form.edges_where({'is_edge': True, 'is_external': False})),
    width=0.1,
)
viewer.draw_reactions(scale=0.1)
viewer.draw_horizontalforces(scale=1.0)

viewer.show()
