from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import rhinoscriptsyntax as rs
import scriptcontext as sc

import compas_rhino
import compas_tna

from compas_tna.diagrams import FormDiagram
from compas_tna.rhino import DiagramHelper


__commandname__ = "TNA_attributes"


def RunCommand(is_interactive):
    if 'TNA' not in sc.sticky:
        raise Exception("Initialise the plugin first!")

    TNA = sc.sticky['TNA']

    options = ['form', 'force']
    option = rs.GetString("Select a Diagram", options[0], options)
    if not option:
        return

    if option == 'form':
        form = TNA['form']
        if not form:
            return

        options = ['vertices', 'edges', 'faces']
        option = rs.GetString("Select a component type", options[0], options)
        if not option:
            return

        if option == 'vertices':
            keys = DiagramHelper.select_vertices(form)
            if not keys:
                return
            if DiagramHelper.update_vertex_attributes(form, keys):
                form.draw(layer=TNA['settings']['layer.form'], clear_layer=True, settings=TNA['settings'])

        elif option == 'edges':
            keys = DiagramHelper.select_edges(form)
            if not keys:
                return
            if DiagramHelper.update_edge_attributes(form, keys):
                form.draw(layer=TNA['settings']['layer.form'], clear_layer=True, settings=TNA['settings'])

        elif option == 'faces':
            keys = DiagramHelper.select_faces(form)
            if not keys:
                return
            if DiagramHelper.update_face_attributes(form, keys):
                form.draw(layer=TNA['settings']['layer.form'], clear_layer=True, settings=TNA['settings'])

    if option == 'force':
        force = TNA['force']
        if not force:
            return

        options = ['vertices', 'edges']
        option = rs.GetString("Select a component type", options[0], options)
        if not option:
            return

        if option == 'vertices':
            keys = DiagramHelper.select_vertices(force)
            if not keys:
                return
            if DiagramHelper.update_vertex_attributes(force, keys):
                force.draw(layer=TNA['settings']['layer.force'], clear_layer=True, settings=TNA['settings'])

        elif option == 'edges':
            keys = DiagramHelper.select_edges(force)
            if not keys:
                return
            if DiagramHelper.update_edge_attributes(force, keys):
                force.draw(layer=TNA['settings']['layer.force'], clear_layer=True, settings=TNA['settings'])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
