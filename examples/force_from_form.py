""""""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import compas_tna

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

form = FormDiagram.from_json(compas_tna.get('form_boundaryconditions.json'))
force  = ForceDiagram.from_formdiagram(form)

force.plot()
