import compas_tna

from compas_tna.diagrams import FormDiagram
from compas_tna.utilities import relax_boundary_openings

FILE = compas_tna.get('tutorial/rhinomesh.obj')

form = FormDiagram.from_obj(FILE)

corners = list(form.vertices_where({'vertex_degree': 2}))

form.edges_attribute('q', 10.0, keys=form.edges_on_boundary())

relax_boundary_openings(form, corners)

form.plot()
