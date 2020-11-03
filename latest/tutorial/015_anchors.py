import compas_tna

from compas_tna.diagrams import FormDiagram

FILE = compas_tna.get('tutorial/rhinomesh.obj')

form = FormDiagram.from_obj(FILE)

corners = list(form.vertices_where({'vertex_degree': 2}))
form.vertices_attribute('is_anchor', True, keys=corners)

form.plot()
