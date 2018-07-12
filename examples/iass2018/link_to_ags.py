from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino
import compas_tna

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.rhino import FormArtist


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2016 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = []


form = FormDiagram.from_obj(compas.get('lines.obj'))

boundaries = form.vertices_on_boundaries()
