""""""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import compas_tna

from compas_tna.diagrams import FormDiagram
from compas_tna.utilities import relax_boundary_openings


form = FormDiagram.from_json(compas_tna.get('formdiagram.json'))

form.set_edges_attribute('q', 10.0, keys=form.edges_on_boundary())
form.set_vertices_attribute('is_fixed', True, keys=form.vertices_where({'vertex_degree': 2}))

relax_boundary_openings(form)

# uncomment to export to json
# filepath = os.path.join(compas_tna.DATA, 'form_unsupported.json')
# form.to_json(filepath)

form.plot()
