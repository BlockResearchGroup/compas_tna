from compas_tna.diagrams import FormDiagram
from compas_fd.fd import fd_numpy


__all__ = [
    "relax_boundary_openings",
    "relax_boundary_openings_proxy",
]


def relax_boundary_openings_proxy(formdata, fixed):
    form = FormDiagram.from_data(formdata)
    relax_boundary_openings(form, fixed)
    return form.to_data()


def relax_boundary_openings(form, fixed):
    k_i = form.vertex_index()
    xyz = form.vertices_attributes("xyz")
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
    fixed = [k_i[key] for key in fixed]
    q = form.edges_attribute("q")
    loads = form.vertices_attributes(("px", "py", "pz"))
    result = fd_numpy(
        vertices=xyz,
        fixed=fixed,
        edges=edges,
        forcedensities=q,
        loads=loads,
    )
    for key in form.vertices():
        index = k_i[key]
        form.vertex_attributes(key, "xyz", result.vertices[index])
