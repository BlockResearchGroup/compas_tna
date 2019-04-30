from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas.plotters import MeshPlotter


form = FormDiagram.from_json('data/boundaryconditions.json')
force  = ForceDiagram.from_formdiagram(form)

# ==============================================================================
# Visualise
# ==============================================================================

plotter = MeshPlotter(force, figsize=(12, 8), tight=True)

vertexcolor = {key: (1.0, 0.9, 0.9) for key in force.vertices() if not form.get_face_attribute(key, 'is_loaded')}

radius = {key: 0.05 for key in force.vertices()}
radius.update({key: 0.1 for key in force.vertices() if not form.get_face_attribute(key, 'is_loaded')})

plotter.draw_vertices(facecolor=vertexcolor, radius=radius)

color = {key: '#00ff00' for key in force.edges() if force.get_form_edge_attribute(form, key, 'is_external')}
width = {key: 2.0 for key in force.edges() if force.get_form_edge_attribute(form, key, 'is_external')}

plotter.draw_edges(color=color, width=width)

plotter.show()
