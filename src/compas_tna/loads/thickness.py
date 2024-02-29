from numpy import array
from scipy.interpolate import griddata

from compas_tna.diagrams import FormDiagram


def distribute_thickness(formdiagram: FormDiagram) -> None:
    """Distribute thickness by interpolating provided values over the vertex grid.

    Parameters
    ----------
    formdiagram : :class:`FormDiagram`

    Returns
    -------
    None
        The missing thickness values are updated directly in the FormDiagram.

    """
    points = []
    values = []
    xi = []
    index_key = {}
    index = 0
    for key in formdiagram.vertices():
        t = formdiagram.vertex_attribute(key, "t")
        xy = formdiagram.vertex_attributes(key, "xy")
        if t:
            points.append(xy)
            values.append(t)
        else:
            xi.append(xy)
            index_key[index] = key
            index += 1
    points = array(points)
    values = array(values)
    xi = array(xi)
    t = griddata(points, values, xi, method="linear")
    t = t.flatten().tolist()
    for index, value in enumerate(t):
        key = index_key[index]
        formdiagram.vertex_attribute(key, "t", value)
