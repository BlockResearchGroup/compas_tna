import compas
import pathlib
from compas_tna.diagrams import FormDiagram
from compas_tna.diagrams import ForceDiagram
from compas_tna.equilibrium import relax_boundary_openings
from compas_tna.equilibrium import horizontal_nodal
from compas_tna.equilibrium import vertical_from_zmax

# for visualisation of the result
from compas.colors import Color
from compas_viewer import Viewer

form = FormDiagram.from_meshgrid(dx=10, nx=10)

corners = list(form.vertices_where(vertex_degree=2))
form.vertices_attribute("is_support", True, keys=corners)

form.edges_attribute("q", 10.0, keys=form.edges_on_boundary())
relax_boundary_openings(form, corners)

form.update_boundaries()

# viewer = Viewer()
# viewer.scene.add(form, color=Color.from_name("lightgray"), 
#                  show_axes=False,
#                  show_grid=False,)
# viewer.show()

force = ForceDiagram.from_formdiagram(form)

horizontal_nodal(form, force, kmax=100)
scale = vertical_from_zmax(form, 3.0)

# viewer = Viewer()
# viewer.scene.add(form)
# viewer.scene.add(force.translated([0.5 * form.aabb().xsize + 0.5 * force.aabb().xsize, 0, 0]))
# viewer.show()

# --------------------------

import math

from compas.colors import Color
from compas.geometry import Cylinder
from compas_tno.analysis import Analysis
from compas_tno.diagrams import FormDiagram as TNODiagram
from compas_tno.shapes import Shape

def visualization(vault, form):
    viewer = Viewer()

    # viewer.scene.add(vault.middle, show_lines=False, name="Middle")
    viewer.scene.add(vault.intrados, show_lines=False, name="Intrados", opacity=0.5)
    viewer.scene.add(vault.extrados, show_lines=False, name="Extrados", opacity=0.5)

    edges = list(form.edges_where({"_is_edge": True}))

    max_thick = 0.1
    forces = [form.edge_attribute(edge, "q") * form.edge_length(edge) for edge in edges]
    fmax = math.sqrt(max(abs(max(forces)), abs(min(forces))))

    pipes = []
    for edge in edges:
        qi = form.edge_attribute(edge, "q")
        line = form.edge_line(edge)
        length = line.length
        force = math.sqrt(abs(qi * length))
        radius = force / fmax * max_thick
        pipe = Cylinder.from_line_and_radius(line, radius)
        if force > 1e-3:
            pipes.append(pipe)
        viewer.scene.add(pipe, color=Color.red())

    # viewer.scene.add(pipes, name="Pipes", color=Color.red())

    viewer.show()

spr_angle = 30.0
L = 10.0
thk = 0.50
xy_span = [[0, L], [0, L]]
vault = Shape.create_crossvault(xy_span=xy_span, thk=thk, spr_angle=30)

TNOForm : TNODiagram = TNODiagram.from_mesh(form)

print(max(TNOForm.q()), min(TNOForm.q()))

analysis = Analysis.create_minthrust_analysis(TNOForm, 
                                              vault, 
                                              printout=True)
# analysis.apply_selfweight()
analysis.apply_envelope()
analysis.set_up_optimiser()
analysis.run()

visualization(vault, TNOForm)