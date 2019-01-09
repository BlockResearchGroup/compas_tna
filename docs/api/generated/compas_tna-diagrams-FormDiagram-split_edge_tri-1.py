import compas
from compas.datastructures import Mesh
from compas.plotters import MeshPlotter
from compas.topology import mesh_quads_to_triangles

mesh = Mesh.from_obj(compas.get('faces.obj'))

mesh_quads_to_triangles(mesh)

u, v = mesh.get_any_edge()

split = mesh.split_edge_tri(u, v)

facecolor = {key: '#cccccc' if key != split else '#ff0000' for key in mesh.vertices()}

plotter = MeshPlotter(mesh)

plotter.draw_vertices(text={key: key for key in mesh.vertices()}, radius=0.2, facecolor=facecolor)
plotter.draw_faces(text={fkey: fkey for fkey in mesh.faces()})

plotter.show()