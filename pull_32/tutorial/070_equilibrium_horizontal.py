import compas_tna

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram
from compas_tna.equilibrium import horizontal_nodal
from compas_plotters import MeshPlotter

FILE = compas_tna.get('tutorial/boundaryconditions.json')

form = FormDiagram.from_json(FILE)
force = ForceDiagram.from_formdiagram(form)

horizontal_nodal(form, force, kmax=100)

# ==============================================================================
# Visualise
# ==============================================================================

plotter = MeshPlotter(force, figsize=(12, 8), tight=True)

vertexcolor = {key: (1.0, 0.9, 0.9) for key in force.vertices() if not form.face_attribute(key, '_is_loaded')}

radius = {key: 0.05 for key in force.vertices()}
radius.update({key: 0.1 for key in force.vertices() if not form.face_attribute(key, '_is_loaded')})

plotter.draw_vertices(facecolor=vertexcolor, radius=radius)

plotter.draw_edges()

plotter.show()
