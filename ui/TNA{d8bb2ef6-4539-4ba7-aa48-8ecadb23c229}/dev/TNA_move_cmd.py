from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import rhinoscriptsyntax as rs
import scriptcontext as sc

import compas_rhino
import compas_tna

from compas_tna.diagrams import FormDiagram
from compas_tna.rhino import DiagramHelper


__commandname__ = "TNA_move"


def RunCommand(is_interactive):
    if 'TNA' not in sc.sticky:
        raise Exception("Initialise the plugin first!")

    TNA = sc.sticky['TNA']
    form = TNA['form']
    force = TNA['force']
    settings = TNA['settings']

    options = ['form', 'force']
    option = rs.GetString("Select a Diagram", options[0], options)
    if not option:
        return

    if option == 'form':
        if not form:
            return

        options = ['vertex', 'vertices', 'diagram']
        option = rs.GetString("Select a component", options[0], options)
        if not option:
            return

        if option == 'vertex':
            key = DiagramHelper.select_vertex(form)
            if key is None:
                return

            if DiagramHelper.move_vertex(form, key):
                form.draw(layer=settings['layer.form'], clear_layer=True, settings=settings)

        elif option == 'vertices':
            keys = DiagramHelper.select_vertices(form)
            if not keys:
                return

            if DiagramHelper.move_vertices(form, keys):
                form.draw(layer=settings['layer.form'], clear_layer=True, settings=settings)

        elif option == 'diagram':
            if DiagramHelper.move(form):
                form.draw(layer=settings['layer.form'], clear_layer=True, settings=settings)

        else:
            raise NotImplementedError

    elif option == 'force':
        if not force:
            return

        options = ['vertex', 'vertices', 'diagram']
        option = rs.GetString("Select a component", options[0], options)
        if not option:
            return

        if option == 'vertex':
            key = DiagramHelper.select_vertex(force)
            if key is None:
                return

            if DiagramHelper.move_vertex(force, key):
                force.draw(layer=settings['layer.force'], clear_layer=True, settings=settings)

        elif option == 'vertices':
            keys = DiagramHelper.select_vertices(force)
            if not keys:
                return

            if DiagramHelper.move_vertices(force, keys):
                force.draw(layer=settings['layer.force'], clear_layer=True, settings=settings)

        elif option == 'diagram':
            if DiagramHelper.move(force):
                force.draw(layer=settings['layer.force'], clear_layer=True, settings=settings)

        else:
            raise NotImplementedError

    else:
        raise NotImplementedError


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
