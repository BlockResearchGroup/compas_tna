import compas

from compas_tna.tna.diagrams.formdiagram import FormDiagram
from compas.datastructures.network.algorithms import find_network_faces

import compas_ags.ags.graphstatics as gs
import compas_tna.tna.algorithms as tna

from compas_tna.viewers.viewer3 import ThrustDiagramViewer


form = FormDiagram.from_obj(compas.get_data('lines.obj'))
form.identify_anchors(anchor_degree=1)

find_network_faces(form, breakpoints=form.breakpoints())

k, m, ind = gs.identify_dof(form)

qind = [5.3275903208784623,
        5.6254187299185912,
        5.3275903208788007,
        5.3275903208788273,
        5.3275903208787438,
        5.6254187299187839,
        5.6254187299188239,
        5.6254187299187235]

for key, attr in form.vertices(True):
    attr['pz'] = 10.

count = 0
for i, (u, v) in enumerate(form.edges()):
    if i in ind:
        form.edge[u][v]['q'] = qind[count]
        count += 1

tna.vertical_from_qind(form, ind, m, density=0.0, display=False)

viewer = ThrustDiagramViewer(form)
viewer.show()
