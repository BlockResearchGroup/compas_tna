import compas

from compas_tna.tna.diagrams.formdiagram import FormDiagram
from compas_tna.tna.diagrams.forcediagram import ForceDiagram

import compas_tna.tna.algorithms as tna

from compas_tna.viewers.viewer3 import ThrustDiagramViewer
from compas_ags.viewers import Viewer


form = FormDiagram.from_obj(compas.get_data('lines.obj'))

form.identify_anchors(anchor_degree=1)
form.set_vertices_attribute('pz', 1.0)

force = ForceDiagram.from_formdiagram(form)

tna.horizontal(form, force, alpha=100, kmax=200, display=False)

viewer = Viewer(form, force, delay_setup=False)
viewer.draw_form()
viewer.draw_force()
viewer.show()

tna.vertical_from_zmax(form, force, zmax=None, density=0.0, display=False)

viewer = ThrustDiagramViewer(form)
viewer.show()
