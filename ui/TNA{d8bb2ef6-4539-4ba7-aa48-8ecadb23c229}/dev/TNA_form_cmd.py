from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import rhinoscriptsyntax as rs
import scriptcontext as sc

import compas_rhino
import compas_tna

from compas_tna.diagrams import FormDiagram


__commandname__ = "TNA_form"


def RunCommand(is_interactive):
    if 'TNA' not in sc.sticky:
        raise Exception("Initialise the plugin first!")

    TNA = sc.sticky['TNA']

    options = ['obj', 'json', 'lines', 'mesh']
    option = rs.GetString("Initialise FormDiagram from", options[0], options)

    if not option:
        return

    if option == 'obj':
        filepath = compas_rhino.select_file(folder=compas_tna.DATA, filter='obj')
        if not filepath:
            return
        form = FormDiagram.from_obj(filepath)

    elif option == 'json':
        filepath = compas_rhino.select_file(folder=compas_tna.DATA, filter='json')
        if not filepath:
            return
        form = FormDiagram.from_json(filepath)

    elif option == 'lines':
        guids = compas_rhino.select_lines()
        if not guids:
            return
        lines = compas_rhino.get_lines_coordinates(guids)
        form = FormDiagram.from_lines(lines)

    elif option == 'mesh':
        guid = compas_rhino.select_mesh()
        if not guid:
            return
        form = FormDiagram.from_rhinomesh(guid)

    else:
        raise NotImplementedError

    form.draw(layer=TNA['settings']['layer.form'], clear_layer=True, settings=TNA['settings'])

    TNA['form'] = form
    TNA['force'] = None


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
