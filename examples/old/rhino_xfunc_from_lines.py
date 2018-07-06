import os
import rhinoscriptsyntax as rs
from compas_tna.tna.diagrams.formdiagram import FormDiagram
from compas_tna.tna.diagrams.forcediagram import ForceDiagram
from compas.utilities import XFunc
from compas_rhino.helpers import network_draw

DIR = os.path.dirname(__file__)
TMP = os.path.join(DIR, '../temp')

guids = rs.ObjectsByLayer('lines')
lines = [[rs.CurveStartPoint(l), rs.CurveEndPoint(l)] for l in guids]
form = FormDiagram.from_lines(lines)
form.identify_anchors(anchor_degree=1)

force = ForceDiagram.from_formdiagram(form)

for fkey in form.face:
    vertices = form.face_vertices(fkey)
    form.set_face_attribute(fkey, 'is_unloaded', vertices[0] != vertices[-1] and len(vertices) > 4)

data = XFunc('compas_tna.tna.algorithms.horizontal_nodal_xfunc',basedir=DIR, tmpdir=TMP)(form.to_data(), force.to_data(), kmax=100)
data = XFunc('compas_tna.tna.algorithms.vertical_from_zmax_xfunc',basedir=DIR, tmpdir=TMP)(data['form'], data['force'], zmax=2.0, kmax=100)

form.data = data['form']
force.data = data['force']

network_draw(form, layer='thrust', clear_layer=True)
network_draw(force, layer='force', clear_layer=True)
