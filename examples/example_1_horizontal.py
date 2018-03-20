import compas

from compas_tna.tna.diagrams.formdiagram import FormDiagram
from compas_tna.tna.diagrams.forcediagram import ForceDiagram
from compas_tna.tna.algorithms.horizontal import horizontal_nodal

from compas_ags.viewers import Viewer


form = FormDiagram.from_obj(compas.get_data('butt_model.obj'))
form.identify_anchors(anchor_degree=1)

force = ForceDiagram.from_formdiagram(form)

for fkey in form.face:
    vertices = form.face_vertices(fkey)
    form.set_face_attribute(fkey, 'is_unloaded', vertices[0] != vertices[-1] and len(vertices) > 4)


for u, v, attr in force.edges(True):
    attr['lmin'] = 1.0
    attr['lmax'] = 3.0


horizontal_nodal(form, force)


for u, v, attr in force.edges(True):
    print attr['lmin'], attr['lmax']


viewer = Viewer(form, force, delay_setup=False)

viewer.default_vertexsize = 0.05

viewer.draw_form()
viewer.draw_force()

viewer.show()
