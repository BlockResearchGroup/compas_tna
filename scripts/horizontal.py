import random

import compas_rhino.objects
import rhinoscriptsyntax as rs
from compas_fd.solvers import fd_numpy

from compas.scene import Scene

# from compas_tna.diagrams import ForceDiagram
from compas_tna.diagrams import FormDiagram

# from compas_tna.equilibrium import horizontal_nodal
from compas_tna.equilibrium import vertical_from_zmax

form = FormDiagram.from_meshgrid(10, 10)

corners = form.vertices_where(vertex_degree=2)
form.vertices_attribute(name="is_support", value=True, keys=corners)

# form.update_boundaries()
# force = ForceDiagram.from_formdiagram(form)
# horizontal_nodal(form, force)

form.edges_attribute(name="q", value=10, keys=form.edges_on_boundary())

# edge = random.choice(form.edges_on_boundary())
# loop = form.edge_loop(edge)
# form.edges_attribute(name="q", value=10, keys=loop)

scene = Scene()
scene.clear()

formobj = scene.add(form, show_forces=False, show_faces=False)
scene.draw()

loads = form.vertices_attributes(names=["px", "py", "pz"])
fixed = list(form.vertices_where(is_support=True))
edges = list(form.edges())

while True:
    rs.UnselectAllObjects()

    guid = compas_rhino.objects.select_curve("Select an edge of the diagram.")
    if not guid:
        break

    guid_edge = {guid: edge for guid, edge in zip(formobj._guids_edges, form.edges())}

    if guid in guid_edge:
        edge = guid_edge[guid]
        loop = form.edge_loop(edge)

        q = rs.GetReal("Force Density", minimum=0, maximum=1000)

        if q is not None:
            form.edges_attribute(name="q", value=q, keys=loop)
            vertices = form.vertices_attributes(names=["x", "y", "z"])
            q = form.edges_attribute("q")

            result = fd_numpy(
                vertices=vertices,
                fixed=fixed,
                edges=edges,
                forcedensities=q,
                loads=loads,
            )

            for vertex, attr in form.vertices(data=True):
                attr["x"] = result.vertices[vertex, 0]
                attr["y"] = result.vertices[vertex, 1]
                attr["z"] = result.vertices[vertex, 2]

            vertical_from_zmax(form, zmax=3)
            formobj.diagram = form

            scene.draw()

formobj.show_faces = True
formobj.show_edges = False

scene.draw()
