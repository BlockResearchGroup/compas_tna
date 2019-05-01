from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import json

import rhinoscriptsyntax as rs
import scriptcontext as sc

import compas_rhino
import compas_tna

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram


__commandname__ = "TNA_file"


def RunCommand(is_interactive):
    if 'TNA' not in sc.sticky:
        raise Exception("Initialise the plugin first!")

    TNA = sc.sticky['TNA']

    form = TNA['form']
    force = TNA['force']

    settings = TNA['settings']

    options = ['save', 'save as', 'open']
    option = rs.GetString("Initialise FormDiagram from", options[0], options)

    if not option:
        return

    if option == 'save':
        if not settings['file.dir']:
            file_dir = compas_rhino.select_folder(default=compas_tna.DATA)
        else:
            file_dir = settings['file.dir']
        if not os.path.isdir(file_dir):
            return

        if not settings['file.name']:
            file_name = rs.GetString('File name')
            if not file_name:
                return
        else:
            file_name = settings['file.name']
        if not file_name.endswith('.json'):
            file_name += '.json'

        filepath = os.path.join(file_dir, file_name)
        if not filepath:
            return

        data = {'settings': settings}

        if form:
            data['form'] = form.to_data()
        if force:
            data['force'] = force.to_data()

        with open(filepath, 'w') as f:
            json.dump(data, f)

    elif option == 'save as':
        file_dir = compas_rhino.select_folder(default=compas_tna.DATA)
        if not file_dir:
            return
        if not os.path.isdir(file_dir):
            return

        file_name = rs.GetString('File name')
        if not file_name:
            return
        if not file_name.endswith('.json'):
            file_name += '.json'

        settings['file.dir'] = file_dir
        settings['file.name'] = file_name

        filepath = os.path.join(file_dir, file_name)
        if not filepath:
            return

        data = {'settings': settings}

        if form:
            data['form'] = form.to_data()
        if force:
            data['force'] = force.to_data()

        with open(filepath, 'w') as f:
            json.dump(data, f)

    elif option == 'open':
        filepath = compas_rhino.select_file(folder=settings['file.dir'], filter='json')
        if not filepath:
            return

        compas_rhino.clear_layer(settings['layer.form'])
        compas_rhino.clear_layer(settings['layer.force'])

        with open(filepath, 'r') as f:
            data = json.load(f)

            settings.update(data['settings'])

            if 'form' in data:
                if data['form']:
                    form = FormDiagram.from_data(data['form'])
                    form.draw(layer=settings['layer.form'], clear_layer=True, settings=settings)
                else:
                    form = None
            else:
                form = None

            if form:
                if 'force' in data:
                    if data['force']:
                        force = ForceDiagram.from_data(data['force'])
                        force.draw(layer=settings['layer.force'], clear_layer=True)
                    else:
                        force = None
                else:
                    force = None

            del TNA['form']
            del TNA['force']

            TNA['form'] = form
            TNA['force'] = force
            TNA['settings'] = settings

    else:
        raise NotImplementedError


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
