""""""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import compas_tna

from compas.utilities import geometric_key
from compas.geometry import distance_point_point_sqrd_xy

from compas_tna.diagrams import FormDiagram
from compas_tna.utilities import relax_boundary_openings


form = FormDiagram.from_json(compas_tna.get('formdiagram.json'))

form.set_edges_attribute('q', 10.0, keys=form.edges_on_boundary())
form.set_vertices_attribute('is_fixed', True, keys=form.vertices_where({'vertex_degree': 2}))

o = form.centroid()

hole = []
for fkey in form.faces():
	c = form.face_centroid(fkey)
	if distance_point_point_sqrd_xy(o, c) < 1.0:
		hole.append(fkey)

for fkey in hole:
	form.delete_face(fkey)

form.cull_vertices()

relax_boundary_openings(form)

# uncomment to export to json
# filepath = os.path.join(compas_tna.DATA, 'form_openings.json')
# form.to_json(filepath)

form.plot()
