from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


from compas.numerical import fd_numpy


__all__ = ['relax_boundary_openings']


def relax_boundary_openings(form):
	k_i   = form.key_index()
	xyz   = form.get_vertices_attributes(('x', 'y', 'z'))
	edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
	fixed = [k_i[key] for key in form.vertices_where({'is_fixed': True})]
	q     = form.get_edges_attribute('q')
	loads = form.get_vertices_attributes(('px', 'py', 'pz'), (0.0, 0.0, 0.0))

	xyz, q, f, l, r = fd_numpy(xyz, edges, fixed, q, loads)

	for key, attr in form.vertices(True):
		index = k_i[key]
		attr['x'] = xyz[index][0]
		attr['y'] = xyz[index][1]
		attr['z'] = xyz[index][2]

