import os

from compas_tna.diagrams import FormDiagram

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, 'data')
FILE = os.path.join(DATA, 'rhinomesh.obj')

form = FormDiagram.from_obj(FILE)

corners = list(form.vertices_where({'vertex_degree': 2}))
form.set_vertices_attribute('is_anchor', True, keys=corners)

form.plot()
