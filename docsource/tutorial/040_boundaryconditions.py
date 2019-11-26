<<<<<<< .merge_file_hD5tYt
from compas_plotters import MeshPlotter
=======
import os
>>>>>>> .merge_file_JrqZuM

from compas_plotters import MeshPlotter
from compas_tna.diagrams import FormDiagram
from compas_tna.utilities import relax_boundary_openings

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, 'data')

FILE_I = os.path.join(DATA, 'rhinomesh.obj')
FILE_O = os.path.join(DATA, 'boundaryconditions.json')

form = FormDiagram.from_obj(FILE_I)

corners = list(form.vertices_where({'vertex_degree': 2}))

form.set_vertices_attribute('is_anchor', True, keys=corners)
form.set_edges_attribute('q', 10.0, keys=form.edges_on_boundary())

relax_boundary_openings(form, corners)

form.update_boundaries(feet=2)

form.to_json(FILE_O)

# ==============================================================================
# Visualisation
# ==============================================================================

plotter = MeshPlotter(form, figsize=(12, 8), tight=True)

vertexcolor = {}
vertexcolor.update({key: '#00ff00' for key in form.vertices_where({'is_fixed': True})})
vertexcolor.update({key: '#0000ff' for key in form.vertices_where({'is_external': True})})
vertexcolor.update({key: '#ff0000' for key in form.vertices_where({'is_anchor': True})})

radius = {key: 0.05 for key in form.vertices()}
radius.update({key: 0.1 for key in form.vertices_where({'is_anchor': True})})

plotter.draw_vertices(
    facecolor=vertexcolor,
    radius=radius
)

plotter.draw_edges(
    keys=list(form.edges_where({'is_edge': True})),
    color={key: '#00ff00' for key in form.edges_where({'is_external': True})},
    width={key: 2.0 for key in form.edges_where({'is_external': True})}
)

plotter.draw_faces(
    facecolor={key: (1.0, 0.9, 0.9) for key in form.faces_where({'is_loaded': False})},
)

plotter.show()
