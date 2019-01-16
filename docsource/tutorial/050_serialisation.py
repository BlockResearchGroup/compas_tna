"""
The data representing a form diagram can be serialised to JSON format
and stored in a file.

The form diagram can be reconstructed from this file without loss of data.

This mechanism is useful to continue working on an unfinished project at a later
time, or to pass data to a different member in your team.

It is also used in Rhino to send information to external processes, for example
to run code that uses libraries that are not available in the dotnet ecosystem.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from compas.plotters import MeshPlotter

from compas_tna.diagrams import FormDiagram
from compas_tna.utilities import relax_boundary_openings


form = FormDiagram.from_obj('data/rhinomesh.obj')

corners = list(form.vertices_where({'vertex_degree': 2}))

form.set_vertices_attributes(('is_anchor', 'is_fixed'), (True, True), keys=corners)
form.set_edges_attribute('q', 10.0, keys=form.edges_on_boundary())

relax_boundary_openings(form)

form.update_boundaries(feet=2)


# save for later

form.to_json('data/boundaryconditions.json')
