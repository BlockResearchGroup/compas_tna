from compas_notebook.scene import ThreeMeshObject

from compas_tna.scene import FormDiagramObject


class ThreeFormObject(ThreeMeshObject, FormDiagramObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self):
        self._guids = []

        vertices = list(self.diagram.vertices())
        faces = list(self.diagram.faces_where(_is_loaded=True))
        edges = list(self.diagram.edges_where(_is_edge=True))

        if self.show_vertices:
            if self.show_vertices is not True:
                vertices = self.show_vertices
            for vertex in self.diagram.vertices_where(is_fixed=True):
                self.vertexcolor[vertex] = self.vertexcolor_fixed
            for vertex in self.diagram.vertices_where(is_support=True):
                self.vertexcolor[vertex] = self.vertexcolor_support
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
