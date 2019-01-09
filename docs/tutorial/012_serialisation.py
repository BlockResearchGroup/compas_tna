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

from compas_tna.diagrams import FormDiagram


# do some initial work

before = FormDiagram.from_obj('data/rhinomesh.obj')

# save for later

before.to_json('data/formdiagram.json')

# weeks or even months go by :)
# and then do some more work...

after = FormDiagram.from_json('data/formdiagram.json')

after.plot()
