import compas

from compas.datastructures import Mesh
from compas.plotters import MeshPlotter

mesh = Mesh.from_obj(compas.get('faces.obj'))

plotter = MeshPlotter(mesh)

plotter.draw_vertices(text={key: key for key in mesh.vertices()}, radius=0.2)
plotter.draw_faces(text={fkey: fkey for fkey in mesh.faces()})

plotter.show()