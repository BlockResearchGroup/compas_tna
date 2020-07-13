from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_rhino.artists import MeshArtist


__all__ = ['ForceArtist']


class ForceArtist(MeshArtist):
    """Artist for force diagrams.

    Parameters
    ----------
    force : :class:`compas_tna.diagrams.ForceDiagram`
        A force diagram.
    layer : str, optional
        The layer in which the artist should draw.
    settings : dict, optional
        Visualisation settings.

    Attributes
    ----------
    settings : dict
        Visualisation settings.

    Examples
    --------
    .. code-block:: python

        from compas_tna.rhino import ForceArtist

        artist = ForceArtist(force, layer='TNA::ForceDiagram')
        artist.draw()

    """

    def __init__(self, force, layer=None, settings=None):
        super(ForceArtist, self).__init__(force, layer=layer)
        self.settings.update({
            'color.vertex': (255, 255, 255),
            'color.edge': (0, 0, 0),
            'color.face': (210, 210, 210),
            'show.vertices': True,
            'show.edges': True,
            'show.faces': False})
        if settings:
            self.settings.update(settings)

    @property
    def force(self):
        return self.datastructure

    def clear(self):
        super(ForceArtist, self).clear()

    def draw(self):
        """Draw the force diagram.

        Notes
        -----
        To change the way individual components are drawn, modify the settings dict of the artist.

        """
        self.clear()
        if self.layer:
            self.clear_layer()
        if self.settings['show.vertices']:
            vertexcolor = {key: self.settings['color.vertices'] for key in self.vertices()}
            self.draw_vertices(color=vertexcolor)
        if self.settings['show.edges']:
            self.draw_edges(
                color=self.settings['color.edges'])
        if self.settings['show.faces']:
            self.draw_faces(
                color=self.settings['color.faces'])
        self.redraw()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
