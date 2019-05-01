from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import rhinoscriptsyntax as rs
import scriptcontext as sc

import compas_rhino
import compas_tna

from compas_tna.diagrams import ForceDiagram


__commandname__ = "TNA_force"


def RunCommand(is_interactive):
    if 'TNA' not in sc.sticky:
        raise Exception("Initialise the plugin first!")

    TNA = sc.sticky['TNA']

    form = TNA['form']
    force = ForceDiagram.from_formdiagram(form)

    del TNA['force']
    TNA['force'] = force

    force.draw(layer=TNA['settings']['layer.force'], clear_layer=True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
