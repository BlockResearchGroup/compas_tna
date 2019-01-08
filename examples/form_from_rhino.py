"""Make a form diagram from Rhino geometry.

Three types of Rhino geometry can be used as input:

* a Rhino surface
* a Rhino mesh
* a set of Rhino lines

.. note::

	Run this example in Rhino with ``form_from_rhino.3dm``.
	This file can be downloaded from github at
	https://raw.githubusercontent.com/BlockResearchGroup/compas_tna/master/data/form_from_rhino.3dm

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import compas_rhino
import compas_tna

from compas_tna.diagrams import FormDiagram
from compas_tna.rhino import FormArtist


guid = compas_rhino.select_mesh()

f1 = FormDiagram.from_rhinomesh(guid, name='FromMesh')

f1.draw(layer='TNA::FormDiagram::Mesh')


guid = compas_rhino.select_surface()

f2 = FormDiagram.from_rhinosurface(guid, name='FromSurf')

f2.draw(layer='TNA::FormDiagram::Surface')


guids = compas_rhino.select_lines()

f3 = FormDiagram.from_rhinolines(guids, name='FromLines')

f3.draw(layer='TNA::FormDiagram::Lines')
