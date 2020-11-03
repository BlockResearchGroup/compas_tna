"""
Make a form diagram from Rhino geometry.
Three types of Rhino geometry can be used as input:

* a Rhino mesh
* a Rhino surface
* a set of Rhino lines

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import compas_rhino

from compas_tna.diagrams import FormDiagram


guid = compas_rhino.select_mesh()

f1 = FormDiagram.from_rhinomesh(guid, name='FromMesh')

f1.draw(layer='TNA::FormDiagram::Mesh')


guid = compas_rhino.select_surface()

f2 = FormDiagram.from_rhinosurface(guid, name='FromSurf')

f2.draw(layer='TNA::FormDiagram::Surface')


guids = compas_rhino.select_lines()

f3 = FormDiagram.from_rhinolines(guids, name='FromLines')

f3.draw(layer='TNA::FormDiagram::Lines')
