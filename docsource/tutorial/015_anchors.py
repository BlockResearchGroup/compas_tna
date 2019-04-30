from compas_tna.diagrams import FormDiagram


form = FormDiagram.from_obj('data/rhinomesh.obj')

corners = list(form.vertices_where({'vertex_degree': 2}))
form.set_vertices_attribute('is_anchor', True, keys=corners)

form.plot()
