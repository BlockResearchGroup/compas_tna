from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino

from compas.geometry import scale_vector
from compas.geometry import length_vector
from compas.geometry import add_vectors
from compas.utilities import i_to_green

from compas_rhino.artists import MeshArtist


__all__ = ['FormArtist']


class FormArtist(MeshArtist):
    """Artist for form diagrams.

    Parameters
    ----------
    form : :class:`compas_tna.diagrams.FormDiagram`
        A form diagram.
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

        from compas_tna.rhino import FormArtist

        artist = FormArtist(form, layer='TNA::FormDiagram')
        artist.draw()

    """

    def __init__(self, form, layer=None, settings=None):
        super(FormArtist, self).__init__(form, layer=layer)
        self.settings.update({
            'color.vertex': (255, 255, 255),
            'color.vertex:is_fixed': (0, 0, 255),
            'color.vertex:is_anchor': (255, 0, 0),
            'color.edge': (0, 0, 0),
            'color.face': (210, 210, 210),
            'color.reaction': (0, 255, 0),
            'color.residual': (0, 255, 255),
            'color.load': (0, 255, 0),
            'color.selfweight': (0, 0, 255),
            'color.force': (0, 0, 255),
            'scale.reaction': 1.0,
            'scale.residual': 1.0,
            'scale.load': 1.0,
            'scale.force': 1.0,
            'scale.selfweight': 1.0,
            'tol.reaction': 1e-3,
            'tol.residual': 1e-3,
            'tol.load': 1e-3,
            'tol.force': 1e-3,
            'tol.selfweight': 1e-3,
            'show.vertices': True,
            'show.edges': True,
            'show.faces': True,
            'show.loads': False,
            'show.reactions': False,
            'show.residuals': False,
            'show.forces': False,
            'show.angles': False})
        if settings:
            self.settings.update(settings)

    @property
    def form(self):
        return self.mesh

    def clear(self):
        super(FormArtist, self).clear()

    def draw(self):
        """Draw the form diagram.

        Notes
        -----
        To change the way individual components are drawn, modify the settings dict of the artist.

        """
        self.clear()
        if self.layer:
            self.clear_layer()
        if self.settings['show.vertices']:
            vertexcolor = {key: self.settings['color.vertices'] for key in self.vertices()}
            vertexcolor.update({key: self.settings['color.vertices:is_fixed'] for key in self.vertices_where({'is_fixed': True})})
            vertexcolor.update({key: self.settings['color.vertices:is_anchor'] for key in self.vertices_where({'is_anchor': True})})
            self.draw_vertices(color=vertexcolor)
        if self.settings['show.edges']:
            self.draw_edges(
                keys=list(self.edges_where({'_is_edge': True})),
                color=self.settings['color.edges'])
        if self.settings['show.faces']:
            self.draw_faces(
                keys=list(self.faces_where({'_is_loaded': True})),
                color=self.settings['color.faces'])
        if self.settings['show.forces']:
            self.draw_forces()
        if self.settings['show.reactions']:
            self.draw_reactions()
        if self.settings['show.angles']:
            self.draw_angles()
        self.redraw()

    def draw_loads(self, scale=None, color=None):
        """Draw the loads.

        Parameters
        ----------
        scale : float, optional
            Scaling factor for the load vectors.
            Default is the value from the settings.
        color : tuple, optional
            RGB color components for load vectors.
            Default is the value from the settings.

        Returns
        -------
        list
            The GUIDs of the created Rhino objects.
        """
        lines = []
        color = color or self.settings['color.load']
        scale = scale or self.settings['scale.load']
        tol = self.settings['tol.load']
        for key in self.form.vertices_where({'is_anchor': False}):
            load = self.form.vertex_attributes(key, ['px', 'py', 'pz'])
            load = scale_vector(load, scale)
            if length_vector(load) < tol:
                continue
            sp = self.form.vertex_coordinates(key)
            ep = add_vectors(sp, load)
            lines.append({
                'start': sp,
                'end': ep,
                'color': color,
                'arrow': 'end',
                'name': "{}.load.{}".format(self.form.name, key)})
        guids = compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)
        self.guids += guids
        return guids

    def draw_selfweight(self, scale=None, color=None):
        """Draw the selfweight.

        Parameters
        ----------
        scale : float, optional
            Scaling factor for the selfweight vectors.
            Default is the value from the settings.
        color : tuple, optional
            RGB color components for selfweight vectors.
            Default is the value from the settings.

        Returns
        -------
        list
            The GUIDs of the created Rhino objects.
        """
        lines = []
        color = color or self.settings['color.selfweight']
        scale = scale or self.settings['scale.selfweight']
        tol = self.settings['tol.selfweight']
        tol2 = tol ** 2
        for key in self.form.vertices_where({'is_anchor': False}):
            t = self.form.vertex_attribute(key, 't')
            a = self.form.vertex_area(key)
            sp = self.form.vertex_coordinates(key)
            dz = scale * t * a
            if dz ** 2 < tol2:
                continue
            ep = [sp[0], sp[1], sp[2] - dz]
            lines.append({
                'start': sp,
                'end': ep,
                'color': color,
                'arrow': 'end',
                'name': "{}.selfweight.{}".format(self.form.name, key)})
        guids = compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)
        self.guids += guids
        return guids

    def draw_reactions(self, scale=None, color=None):
        """Draw the reactions.

        Parameters
        ----------
        scale : float, optional
            Scaling factor for the reaction vectors.
            Default is the value from the settings.
        color : tuple, optional
            RGB color components for reaction vectors.
            Default is the value from the settings.

        Returns
        -------
        list
            The GUIDs of the created Rhino objects.
        """
        lines = []
        color = color or self.settings['color.reaction']
        scale = scale or self.settings['scale.reaction']
        tol = self.settings['tol.reaction']
        for key in self.form.vertices_where({'is_anchor': True}):
            reaction = self.form.vertex_attributes(key, ['_rx', '_ry', '_rz'])
            reaction = scale_vector(reaction)
            if length_vector(reaction) < tol:
                continue
            sp = self.form.vertex_coordinates(key)
            ep = add_vectors(sp, reaction)
            lines.append({
                'start': sp,
                'end': ep,
                'color': color,
                'arrow': 'start',
                'name': "{}.reaction.{}".format(self.form.name, key)})
        guids = compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)
        self.guids += guids
        return guids

    def draw_forces(self, scale=None, color=None):
        """Draw the forces.

        Parameters
        ----------
        scale : float, optional
            Scaling factor for the force pipes.
            Default is the value from the settings.
        color : tuple, optional
            RGB color components for force pipes.
            Default is the value from the settings.

        Returns
        -------
        list
            The GUIDs of the created Rhino objects.
        """
        lines = []
        color = color or self.settings['color.force']
        scale = scale or self.settings['scale.force']
        tol = self.settings['tol.force']
        for u, v in self.form.edges_where({'_is_edge': True}):
            force = self.form.edge_attribute((u, v), '_f')
            sp, ep = self.form.edge_coordinates(u, v)
            radius = scale * force
            if radius < tol:
                continue
            lines.append({
                'start': sp,
                'end': ep,
                'radius': radius,
                'color': color,
                'name': "{}.force.{}-{}".format(self.form.name, u, v)})
        guids = compas_rhino.draw_cylinders(lines, layer=self.layer, clear=False, redraw=False)
        self.guids += guids
        return guids

    def draw_residuals(self, scale=None, color=None):
        """Draw the residual forces.

        Parameters
        ----------
        scale : float, optional
            Scaling factor for the force vectors.
            Default is the value from the settings.
        color : tuple, optional
            RGB color components for force vectors.
            Default is the value from the settings.

        Returns
        -------
        list
            The GUIDs of the created Rhino objects.
        """
        lines = []
        color = color or self.settings['color.residual']
        scale = scale or self.settings['scale.residual']
        tol = self.settings['tol.residual']
        for key in self.form.vertices_where({'is_anchor': False}):
            residual = self.form.vertex_attributes(key, ['_rx', '_ry', '_rz'])
            residual = scale_vector(residual, scale)
            if length_vector(residual) < tol:
                continue
            sp = self.form.vertex_coordinates(key)
            ep = add_vectors(sp, residual)
            lines.append({
                'start': sp,
                'end': ep,
                'color': color,
                'arrow': 'start',
                'name': "{}.residual.{}".format(self.form.name, key)})
        guids = compas_rhino.draw_lines(lines, layer=self.layer, clear=False, redraw=False)
        self.guids += guids
        return guids

    def draw_angles(self, tol=5.0):
        """Draw the angle deviations.

        Parameters
        ----------
        tol : float, optional
            Tolerance value for angle deviations.
            Default value is ``5.0``.

        Returns
        -------
        list
            The GUIDs of the created Rhino objects.
        """
        labels = []
        for u, v in self.form.edges_where({'_is_edge': True}):
            a_rad = self.form.edge_attribute((u, v), '_a')
            a_deg = 180 * a_rad / 3.14159
            if a_deg > tol:
                color = i_to_green(a_rad / tol)
                labels.append({
                    'pos': self.form.edge_midpoint(u, v),
                    'text': "{:.1f}".format(a_deg),
                    'color': color,
                    'name': "{}.angle.{}-{}".format(self.form.name, u, v)})
        guids = compas_rhino.draw_labels(labels, layer=self.layer, clear=False, redraw=False)
        self.guids += guids
        return guids


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
