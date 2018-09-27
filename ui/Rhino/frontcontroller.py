from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import json

import compas
import compas_rhino
import compas_tna

from compas.utilities import now

from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram

from compas_tna.rhino import FormArtist

from actions import FormActions
from actions import ForceActions
from actions import EquilibriumActions
from actions import VisualisationActions

HERE = os.path.abspath(os.path.dirname(__file__))

try:
    import rhinoscriptsyntax as rs
except ImportError:
    pass


__all__ = ['TNAFrontController']


class TNAFrontController(VisualisationActions,
                         EquilibriumActions,
                         ForceActions,
                         FormActions):

    instancename = 'tna'

    def __init__(self):
        self.form = None
        self.force = None
        self.settings = {
            'current_working_directory' : None,

            'form.layer'                : 'TNA::FormDiagram',
            'force.layer'               : 'TNA::ForceDiagram',

            'horizontal.alpha'          : 100,
            'horizontal.kmax'           : 200,
            'vertical.zmax'             : 3,
        }

    @property
    def cwd(self):
        cwd = self.settings['current_working_directory']
        if not cwd or not os.path.exists(cwd):
            cwd = HERE
        return cwd

    @cwd.setter
    def cwd(self, path):
        self.settings['current_working_directory'] = path

    def init(self):
        compas_rhino.clear_layers([self.settings['form.layer'], self.settings['force.layer']])

    def update_settings(self):
        compas_rhino.update_settings(self.settings)

    def save(self):
        folder = compas_rhino.select_folder(default=self.cwd)
        if not folder:
            return
        self.cwd = folder
        name = rs.GetString("Name of the project", "compas_tna-{}.json".format(now()))
        if not name:
            return
        name = coerce_json(name)
        data = {
            'form'     : self.form.to_data(),
            'force'    : self.force.to_data(),
            'settings' : self.settings
        }
        with open(os.path.join(folder, name), 'w+') as fo:
            json.dump(data, fo)

    def load(self):
        path = compas_rhino.select_file(folder=self.cwd, filter='JSON files (*.json)|*.json||')
        if not path:
            return
        with open(path, 'r') as fo:
            data = json.load(fo)
        settings = data.get('settings')
        formdata = data.get('form')
        forcedata = data.get('force')
        if settings:
            self.settings.update(settings)
        if formdata:
            self.form = FormDiagram.from_data(formdata)
            self.form.draw(layer=self.settings['layer'])
        if forcedata:
            self.force = ForceDiagram.from_data(forcedata)
            self.force.draw(layer=self.settings['layer'])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
