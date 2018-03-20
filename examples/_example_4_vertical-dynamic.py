import random
import compas

from compas.utilities.colors import i_to_rgb
from compas.datastructures.network.viewer import NetworkViewer
from compas.viewers.drawing import xdraw_points
from compas.viewers.drawing import xdraw_lines

from compas_tna.diagrams.formdiagram import FormDiagram

import compas_tna.algorithms as tna


class ThrustNetworkViewer(NetworkViewer):

    def __init__(self, form, ind, m):
        super(ThrustNetworkViewer, self).__init__(form)
        self.form = form
        self.ind = ind
        self.m = m

    def timer(self, v):
        qind = random.sample(xrange(20, 80), len(self.ind))
        print qind
        i = 0
        for index, u, v in self.form.edges_enum():
            if index in self.ind:
                self.form.edge[u][v]['q'] = 0.1 * qind[i]
                i += 1
        tna.vertical_from_qind(self.form, self.ind, self.m, density=0.0, display=False)

    def display(self):
        points  = []
        color = to_rgb(self.network.attributes['color.vertex'], True)
        color_support = to_rgb(self.network.attributes['color.vertex:is_anchor'], True)
        for i, _, attr in self.network.vertices_enum(True):
            points.append({
                'pos'  : (attr['x'], attr['y'], attr['z']),
                'size' : 10.,
                'color': color_support if attr['is_anchor'] else color,
            })
        lines = []
        color = to_rgb(self.network.attributes['color.edge'], True)
        color_ind = 0.0, 1.0, 0.0
        for i, u, v in self.network.edges_enum():
            lines.append({
                'start': self.network.vertex_coordinates(u),
                'end'  : self.network.vertex_coordinates(v),
                'color': color_ind if i in self.ind else color,
                'width': 1 if i not in self.ind else int(0.1 * self.ind[self.ind.index(i)])
            })
        xdraw_points(points)
        xdraw_lines(lines)


# ==============================================================================
# init
# ==============================================================================

form = FormDiagram.from_obj(compas.get_data('lines.obj'))

form.identify_anchors(anchor_degree=1)
form.identify_faces()

# rename to
# set_vertex_attribute_all()
form.set_vertices_attribute('pz', 10.0)

# ==============================================================================
# DOF
# ==============================================================================

k, m, ind = form.dof(identify=True)

# ==============================================================================
# zmax => scale
# ==============================================================================

viewer = ThrustNetworkViewer(form, ind, m)
viewer._timeout = 1000
viewer.setup()
viewer.show()
