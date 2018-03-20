import compas
import compas_rhino

from compas_tna.tna.diagrams.formdiagram import FormDiagram
from compas_tna.tna.diagrams.forcediagram import ForceDiagram

from compas.utilities import XFunc

horizontal_nodal = XFunc('compas_tna.tna.algorithms.horizontal.horizontal_nodal_xfunc')

form = FormDiagram.from_obj(compas.get_data('butt_model.obj'))
form.identify_anchors(anchor_degree=1)

force = ForceDiagram.from_formdiagram(form)

for fkey in form.face:
    vertices = form.face_vertices(fkey)
    form.set_face_attribute(fkey, 'is_unloaded', vertices[0] != vertices[-1] and len(vertices) > 4)

res = horizontal_nodal(form.to_data(), force.to_data(), kmax=100)

if res['error']:
    print res['error']
else:
    print res['profile']
    form.data = res['data']['form']
    force.data = res['data']['force']
    
    compas_rhino.draw_network(form, layer='FormDiagram', clear_layer=True)
    compas_rhino.draw_network(force, layer='ForceDiagram', clear_layer=True)
