from typing import List

from compas_fd.solvers import fd_numpy

from compas_tna.diagrams import FormDiagram


def relax_boundary_openings(form: FormDiagram, fixed: List[int]) -> FormDiagram:
    """Relax the FormDiagram to create a smooth starting geometry with inward curving unsupported boundaries.

    Parameters
    ----------
    form : :class:`Formdiagram`
        The FormDiagram.
    fixed : list[int]
        The fixed vertices of the diagram.

    Returns
    -------
    :class:`FormDiagram`
        The diagram is updated in place, but the updated diagram is also returned
        for compatibility with RPC calls.

    """
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
    return form
