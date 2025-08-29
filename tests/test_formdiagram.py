from compas_tna.diagrams import FormDiagram


def test_from_meshgrid():
    formdiagram = FormDiagram.from_meshgrid(10, 10)

    assert formdiagram.number_of_faces() == 100


def test_corner_supports():
    formdiagram: FormDiagram = FormDiagram.from_meshgrid(10, 10)  # type: ignore

    corners = list(formdiagram.vertices_where(vertex_degree=2))
    formdiagram.vertices_attribute("is_support", True, keys=corners)

    assert len(list(formdiagram.supports())) == 4
