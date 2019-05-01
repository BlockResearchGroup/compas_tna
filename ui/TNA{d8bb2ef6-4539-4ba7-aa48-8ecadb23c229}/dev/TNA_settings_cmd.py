from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import scriptcontext as sc
import compas_rhino

__commandname__ = "TNA_settings"


def RunCommand(is_interactive):
    if 'TNA' not in sc.sticky:
        raise Exception("Initialise the plugin first!")

    TNA = sc.sticky['TNA']

    form = TNA['form']
    force = TNA['force']

    if compas_rhino.update_settings(TNA['settings']):
        if form:
            form.draw(layer=TNA['settings']['layer.form'], clear_layer=True, settings=TNA['settings'])
        if force:
            force.draw(layer=TNA['settings']['layer.force'], clear_layer=True)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
