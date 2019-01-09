"""
Preprocess the unsupported boundary openings of a FormDiagram.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas_tna.diagrams import FormDiagram
from compas_tna.utilities import relax_boundary_openings


form = FormDiagram.from_obj('data/rhinomesh.obj')

corners = list(form.vertices_where({'vertex_degree': 2}))

form.set_vertices_attribute('is_fixed', True, keys=corners)
form.set_edges_attribute('q', 10.0, keys=form.edges_on_boundary())

relax_boundary_openings(form)

form.plot()
