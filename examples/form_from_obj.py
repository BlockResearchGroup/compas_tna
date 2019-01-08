"""Make a form diagram from an obj file.

.. note::

	OBJ files can be used to work outside of Rhino, using the plotters for visualisation.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import compas_tna

from compas_tna.diagrams import FormDiagram


form = FormDiagram.from_obj(compas_tna.get('rhinomesh.obj'))

corners = list(form.vertices_where({'vertex_degree': 2}))

form.set_vertices_attribute('is_anchor', True, keys=corners)

# uncomment to export to json
filepath = os.path.join(compas_tna.DATA, 'form_from_obj.json')
form.to_json(filepath)

form.plot()
