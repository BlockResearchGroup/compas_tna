import compas_tna

from compas_plotters import MeshPlotter
from compas_tna.diagrams import FormDiagram
from compas_tna.utilities import relax_boundary_openings

FILE_I = compas_tna.get('tutorial/rhinomesh.obj')
FILE_O = compas_tna.get('tutorial/boundaryconditions.json')

form = FormDiagram.from_obj(FILE_I)

corners = list(form.vertices_where({'vertex_degree': 2}))

form.vertices_attribute('is_anchor', True, keys=corners)
form.edges_attribute('q', 10.0, keys=form.edges_on_boundary())

relax_boundary_openings(form, corners)

form.update_boundaries()

form.to_json(FILE_O)

# ==============================================================================
# Visualisation
# ==============================================================================

plotter = MeshPlotter(form, figsize=(12, 8), tight=True)

vertexcolor = {}
vertexcolor.update({key: '#00ff00' for key in form.vertices_where({'is_fixed': True})})
vertexcolor.update({key: '#ff0000' for key in form.vertices_where({'is_anchor': True})})

radius = {key: 0.05 for key in form.vertices()}
radius.update({key: 0.1 for key in form.vertices_where({'is_anchor': True})})

plotter.draw_vertices(
    facecolor=vertexcolor,
    radius=radius)

edges = list(form.edges_where({'_is_edge': True}))
plotter.draw_edges(
    keys=edges)

faces = list(form.faces_where({'_is_loaded': True}))

plotter.draw_faces(
    keys=faces, facecolor=(1.0, 0.9, 0.9),)

plotter.show()
