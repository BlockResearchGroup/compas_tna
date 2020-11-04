import compas_tna

from compas_tna.diagrams import FormDiagram

FILE = compas_tna.get('tutorial/rhinomesh.obj')

form = FormDiagram.from_obj(FILE)

form.plot()
