"""
Make a form diagram from the data contained in an OBJ file.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import compas_tna

from compas_tna.diagrams import FormDiagram


form = FormDiagram.from_obj(compas_tna.get('rhinomesh.obj'))

form.plot()
