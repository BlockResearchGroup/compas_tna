import compas

from compas_tna.tna.diagrams.formdiagram import FormDiagram
from compas_ags.ags.graphstatics import identify_dof

from compas.visualization.plotters.networkplotter import NetworkPlotter

formdiagram = FormDiagram.from_obj(compas.get_data('lines.obj'))
formdiagram.identify_anchors(anchor_degree=1)

k, m, ind = identify_dof(formdiagram)

assert k == len(ind), 'the number of independent edges is not correct: k = {0} != len(ind) = {1}'.format(k, len(ind))

vcolor = {key: '#ff0000' for key, attr in formdiagram.vertices(True) if attr['is_anchor']}
ecolor = {(u, v): '#00ff00' for i, (u, v) in enumerate(formdiagram.edges()) if i in ind}

plotter = NetworkPlotter(formdiagram)

plotter.defaults['face.facecolor'] = '#eeeeee'
plotter.defaults['face.edgewidth'] = 0.0

plotter.draw_vertices(facecolor=vcolor,
                      text={key: key for key in formdiagram.vertices()},
                      radius=0.2)

plotter.draw_edges(color=ecolor)

plotter.show()
