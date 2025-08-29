from compas_fd.solvers import fd_numpy

from compas_tna.diagrams import FormDiagram


def relax_boundary_openings(form: FormDiagram, fixed: list[int]) -> FormDiagram:
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
    xyz: list[list[float]] = form.vertices_attributes("xyz")  # type: ignore
    edges = [(k_i[u], k_i[v]) for u, v in form.edges()]
    fixed = [k_i[key] for key in fixed]
    q: list[float] = form.edges_attribute("q")  # type: ignore
    loads: list[list[float]] = form.vertices_attributes(("px", "py", "pz"))  # type: ignore
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
