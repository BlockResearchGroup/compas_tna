import scriptcontext as sc  # type: ignore
from compas_rhino.conversions import line_to_rhino
from compas_rhino.scene import RhinoMeshObject

from compas_tna.scene import FormDiagramObject


class RhinoFormObject(RhinoMeshObject, FormDiagramObject):
    def draw(self):
        self._guids = []

        if self.show_vertices:
            for vertex in self.diagram.vertices_where(is_fixed=True):
                self.vertexcolor[vertex] = self.vertexcolor_fixed

            for vertex in self.diagram.vertices_where(is_support=True):
                self.vertexcolor[vertex] = self.vertexcolor_support

            self._guids += self.draw_vertices()

        if self.show_edges:
            if self.show_edges is True:
                self.show_edges = list(self.diagram.edges_where(_is_edge=True))

            self._guids += self.draw_edges()

        if self.show_faces:
            if self.show_faces is True:
                self.show_faces = list(self.diagram.faces_where(_is_loaded=True))

            self._guids += self.draw_faces()

        self._guids += self.draw_loads()
        self._guids += self.draw_selfweight()
        self._guids += self.draw_reactions()
        self._guids += self.draw_residuals()

        # self._guids += self.draw_forces()
        # self._guids += self.draw_angles()

        return self.guids

    # =============================================================================
    # Helpers
    # =============================================================================

    def draw_loads(self):
        guids = []
        if not self.show_loads:
            return guids

        for vertex in self.diagram.vertices_where(is_support=False):
            load = self.diagram.vertex_load(vertex)
            load.scale(self.scale_load)

            if load.length < self.tol_load:
                continue

            sp = self.diagram.vertex_point(vertex)
            ep = sp + load

            attr = self.compile_attributes(
                name="{}.load.{}".format(self.diagram.name, vertex),
                color=self.color_load,
                arrow="end",
            )
            geometry = line_to_rhino((sp, ep))
            guids.append(sc.doc.Objects.AddLine(geometry, attr))

        return guids

    def draw_selfweight(self):
        guids = []
        if not self.show_selfweight:
            return guids

        for vertex in self.diagram.vertices_where(is_support=False):
            selfweight = self.diagram.vertex_selfweight(vertex)
            selfweight.scale(self.scale_selfweight)

            if selfweight.length < self.tol_selfweight:
                continue

            sp = self.diagram.vertex_point(vertex)
            ep = sp + selfweight

            attr = self.compile_attributes(
                name="{}.selfweight.{}".format(self.diagram.name, vertex),
                color=self.color_selfweight,
                arrow="end",
            )
            geometry = line_to_rhino((sp, ep))
            guids.append(sc.doc.Objects.AddLine(geometry, attr))

        return guids

    def draw_reactions(self):
        guids = []
        if not self.show_reactions:
            return guids

        for vertex in self.diagram.vertices_where(is_support=True):
            reaction = self.diagram.vertex_reaction(vertex)
            reaction.scale(self.scale_reaction)

            if reaction.length < self.tol_reaction:
                continue

            sp = self.diagram.vertex_point(vertex)
            ep = sp + reaction

            attr = self.compile_attributes(
                name="{}.reaction.{}".format(self.diagram.name, vertex),
                color=self.color_reaction,
                arrow="end",
            )
            geometry = line_to_rhino((sp, ep))
            guids.append(sc.doc.Objects.AddLine(geometry, attr))

        return guids

    def draw_residuals(self):
        guids = []
        if not self.show_residuals:
            return guids

        for vertex in self.diagram.vertices_where(is_support=False):
            residual = self.diagram.vertex_residual(vertex)
            residual.scale(self.scale_residual)

            if residual.length < self.tol_residual:
                continue

            sp = self.diagram.vertex_point(vertex)
            ep = sp + residual

            attr = self.compile_attributes(
                name="{}.residual.{}".format(self.diagram.name, vertex),
                color=self.color_residual,
                arrow="end",
            )
            geometry = line_to_rhino((sp, ep))
            guids.append(sc.doc.Objects.AddLine(geometry, attr))

        return guids

    # def draw_forces(self, scale=None, color=None):
    #     """Draw the forces.

    #     Parameters
    #     ----------
    #     scale : float, optional
    #         Scaling factor for the force pipes.
    #         Default is the value from the settings.
    #     color : tuple, optional
    #         RGB color components for force pipes.
    #         Default is the value from the settings.

    #     Returns
    #     -------
    #     list
    #         The GUIDs of the created Rhino objects.
    #     """
    #     lines = []
    #     color = color or self.settings["color.force"]
    #     scale = scale or self.settings["scale.force"]
    #     tol = self.settings["tol.force"]
    #     for u, v in self.diagram.edges_where({"_is_edge": True}):
    #         force = self.diagram.edge_attribute((u, v), "_f")
    #         sp, ep = self.diagram.edge_coordinates(u, v)
    #         radius = scale * force
    #         if radius < tol:
    #             continue
    #         lines.append(
    #             {
    #                 "start": sp,
    #                 "end": ep,
    #                 "radius": radius,
    #                 "color": color,
    #                 "name": "{}.force.{}-{}".format(self.diagram.name, u, v),
    #             }
    #         )
    #     guids = compas_rhino.draw_cylinders(
    #         lines, layer=self.layer, clear=False, redraw=False
    #     )
    #     self.guids += guids
    #     return guids

    # def draw_angles(self, tol=5.0):
    #     """Draw the angle deviations.

    #     Parameters
    #     ----------
    #     tol : float, optional
    #         Tolerance value for angle deviations.
    #         Default value is ``5.0``.

    #     Returns
    #     -------
    #     list
    #         The GUIDs of the created Rhino objects.
    #     """
    #     labels = []
    #     for u, v in self.diagram.edges_where({"_is_edge": True}):
    #         a_rad = self.diagram.edge_attribute((u, v), "_a")
    #         a_deg = 180 * a_rad / 3.14159
    #         if a_deg > tol:
    #             color = i_to_green(a_rad / tol)
    #             labels.append(
    #                 {
    #                     "pos": self.diagram.edge_midpoint(u, v),
    #                     "text": "{:.1f}".format(a_deg),
    #                     "color": color,
    #                     "name": "{}.angle.{}-{}".format(self.diagram.name, u, v),
    #                 }
    #             )
    #     guids = compas_rhino.draw_labels(
    #         labels, layer=self.layer, clear=False, redraw=False
    #     )
    #     self.guids += guids
    #     return guids
