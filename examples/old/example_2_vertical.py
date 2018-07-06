import compas
from compas_tna.tna.diagrams.formdiagram import FormDiagram
from compas_tna.tna.diagrams.forcediagram import ForceDiagram
import compas_tna.tna.algorithms as tna
from compas.viewers import NetworkViewer


form = FormDiagram.from_obj(compas.get_data('lines.obj'))

form.identify_anchors(anchor_degree=1)
form.set_vertices_attribute('pz', 1.0)

force = ForceDiagram.from_formdiagram(form)
tna.horizontal(form, force, alpha=100, kmax=200, display=False)
# viewer = NetworkViewer(force, 600, 600)
# viewer.setup()
# viewer.show()
tna.vertical_from_zmax(form, force, zmax=2, density=0.0, display=False)
viewer = NetworkViewer(form, 600, 600)
viewer.setup()
viewer.show()
