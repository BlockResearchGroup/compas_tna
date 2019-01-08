""""""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import compas_tna

from compas_tna.diagrams import FormDiagram


form = FormDiagram.from_json(compas_tna.get('form_from_obj.json'))

form.plot()
