from compas_notebook.scene import ThreeMeshObject

from compas_tna.scene import ForceDiagramObject


class ThreeForceObject(ThreeMeshObject, ForceDiagramObject):
    def draw(self):
        self._guids = []

        vertices = list(self.diagram.vertices())
        faces = list(self.diagram.faces())
        edges = list(self.diagram.edges())

        if self.show_vertices:
            if self.show_vertices is not True:
                vertices = self.show_vertices
            self._guids.append(self.draw_vertices(vertices, self.vertexcolor))

        if self.show_edges:
            if self.show_edges is not True:
                edges = self.show_edges
            self._guids.append(self.draw_edges(edges, self.edgecolor))

        if self.show_faces:
            if self.show_faces is not True:
                faces = self.show_faces
            self._guids.append(self.draw_faces(faces, self.facecolor))

        return self.guids
