import compas_tna

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram
from compas_tna.equilibrium import horizontal_nodal
from compas_tna.equilibrium import vertical_from_zmax
from compas_plotters import MeshPlotter
from compas.utilities import i_to_black

FILE = compas_tna.get('tutorial/boundaryconditions.json')

form = FormDiagram.from_json(FILE)
force = ForceDiagram.from_formdiagram(form)

horizontal_nodal(form, force, alpha=100)
scale = vertical_from_zmax(form, 3.0)

# ==============================================================================
# visualise
# ==============================================================================

# draw pipe diagram
# and actual reaction forces

z = form.vertices_attribute('z')
zmin = min(z)
zmax = max(z)

plotter = MeshPlotter(form, figsize=(12, 8), tight=True)

plotter.draw_vertices(
    keys=list(form.vertices()),
    facecolor={key: i_to_black((attr['z'] - zmin) / (zmax - zmin)) for key, attr in form.vertices(True)},
    radius=0.1
)

plotter.draw_edges(
    keys=list(form.edges_where({'_is_edge': True}))
)

plotter.draw_faces(keys=list(form.faces_where({'_is_loaded': True})))

plotter.show()
