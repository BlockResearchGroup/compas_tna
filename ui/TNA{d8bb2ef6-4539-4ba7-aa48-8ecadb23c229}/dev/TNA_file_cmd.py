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


def get_document_basename():
    return rs.DocumentName()


def get_document_filename():
    basename = get_document_basename()
    if not basename:
        return None
    return os.path.splitext(basename)[0]


def get_document_extension():
    basename = get_document_basename()
    if not basename:
        return None
    return os.path.splitext(basename)[1]


def get_document_filepath():
    return rs.DocumentPath()


def get_document_dirname():
    filepath = get_document_filepath()
    if not filepath:
        return None
    return os.path.dirname(filepath)


# ==============================================================================
# Command
# ==============================================================================


HERE = get_document_dirname()


def RunCommand(is_interactive):
    if 'TNA' not in sc.sticky:
        raise Exception("Initialise the plugin first!")

    TNA = sc.sticky['TNA']

    form = TNA['form']
    force = TNA['force']

    settings = TNA['settings']

    options = ['save', 'save_as', 'open']
    option = rs.GetString("Initialise FormDiagram from", options[0], options)

    if not option:
        return

    if option == 'save':
        # save the current file in the current directory

        # get the components of the current filepath
        if not settings['file.dir']:
            file_dir = compas_rhino.select_folder(default=HERE)
        else:
            file_dir = compas_rhino.select_folder(default=settings['file.dir'])

        if not os.path.isdir(file_dir):
            print('The selected directory is invalid: {}'.format(file_dir))
            return

        settings['file.dir'] = file_dir

        if not settings['file.name']:
            file_name = compas_rhino.select_file(folder=settings['file.dir'])
            if not file_name:
                print('The filename is invalid: {}'.format(file_name))
                return
            settings['file.name'] = file_name

        file_name = settings['file.name']

        if not file_name.endswith('.json'):
            print('The filename is invalid: {}'.format(file_name))
            return

        # compile the filepath
        filepath = os.path.join(file_dir, file_name)

        # compile the data dict
        data = {'settings': settings}
        if form:
            data['form'] = form.to_data()
        if force:
            data['force'] = force.to_data()

        # write the data dict to the specified file
        with open(filepath, 'w') as f:
            json.dump(data, f)

    elif option == 'save_as':
        # save the current file using a different name and location

        # get the components of the current filepath
        if not settings['file.dir']:
            file_dir = compas_rhino.select_folder(default=HERE)
        else:
            file_dir = compas_rhino.select_folder(default=settings['file.dir'])

        settings['file.dir'] = file_dir

        if not os.path.isdir(file_dir):
            print('The selected directory is invalid: {}'.format(file_dir))
            return

        file_name = rs.GetString('File name')
        if not file_name:
            print('The filename is invalid: {}'.format(file_name))
            return

        if not file_name.endswith('.json'):
            print('The filename is invalid: {}'.format(file_name))
            return

        settings['file.dir'] = file_dir
        settings['file.name'] = file_name

        if not file_name.endswith('.json'):
            print('The filename is invalid: {}'.format(file_name))
            return

        # compile the filepath
        filepath = os.path.join(file_dir, file_name)

        data = {'settings': settings}

        if form:
            data['form'] = form.to_data()
        if force:
            data['force'] = force.to_data()

        with open(filepath, 'w') as f:
            json.dump(data, f)

    elif option == 'open':
        # open a specified file
        # and update the current file properties in the settings

        # get the dirname of the current filepath
        if not settings['file.dir']:
            filepath = compas_rhino.select_file(folder=HERE, filter='json')
        else:
            filepath = compas_rhino.select_file(folder=settings['file.dir'], filter='json')

        if not filepath:
            return

        file_dir = os.path.dirname(filepath)
        file_name = os.path.basename(filepath)

        settings['file.dir'] = file_dir
        settings['file.name'] = file_name

        if not file_name.endswith('.json'):
            print('The filename is invalid: {}'.format(file_name))
            return

        # compile the filepath
        filepath = os.path.join(file_dir, file_name)

        compas_rhino.clear_layer(settings['layer.form'])
        compas_rhino.clear_layer(settings['layer.force'])

        with open(filepath, 'r') as f:
            data = json.load(f)

            settings.update(data['settings'])

            if 'form' in data and data['form']:
                form = FormDiagram.from_data(data['form'])
                form.draw(layer=settings['layer.form'], clear_layer=True, settings=settings)
            else:
                form = None

            if form and 'force' in data and data['force']:
                force = ForceDiagram.from_data(data['force'])
                force.draw(layer=settings['layer.force'], clear_layer=True)
            else:
                force = None

            del TNA['form']
            del TNA['force']

            TNA['form'] = form
            TNA['force'] = force
            TNA['settings'] = settings

    else:
        # any other options are invalid
        raise NotImplementedError


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    RunCommand(True)
