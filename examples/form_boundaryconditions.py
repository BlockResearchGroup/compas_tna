""""""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import compas_tna

from compas_tna.diagrams import FormDiagram
from compas.plotters import MeshPlotter

form = FormDiagram.from_json(compas_tna.get('form_openings.json'))

form.attributes['feet.scale'] = 1.0

form.update_boundaries(feet=2)

# form.plot()

plotter = MeshPlotter(form, figsize=(12, 8), tight=True)

vertexcolor = {}
vertexcolor.update({key: '#00ff00' for key in form.vertices_where({'is_fixed': True})})
vertexcolor.update({key: '#0000ff' for key in form.vertices_where({'is_external': True})})
vertexcolor.update({key: '#ff0000' for key in form.vertices_where({'is_anchor': True})})

radius = {key: 0.05 for key in form.vertices()}
radius.update({key: 0.1 for key in form.vertices_where({'is_anchor': True})})

plotter.draw_vertices(
	facecolor=vertexcolor,
	radius=radius
)

plotter.draw_edges(
	keys=list(form.edges_where({'is_edge': True})),
	color={key: '#00ff00' for key in form.edges_where({'is_external': True})},
	width={key: 2.0 for key in form.edges_where({'is_external': True})}
)

plotter.draw_faces(
	facecolor={key: (1.0, 0.9, 0.9) for key in form.faces_where({'is_loaded': False})},
	text={key: str(key) for key in form.faces_where({'is_loaded': False})}
)

# uncomment to export to json
# filepath = os.path.join(compas_tna.DATA, 'form_boundaryconditions.json')
# form.to_json(filepath)

plotter.show()
