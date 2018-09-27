from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os

import compas
import compas_rhino
import compas_tna

from compas.geometry import mesh_smooth_area
from compas.geometry import mesh_smooth_centroid

from compas_tna.diagrams import FormDiagram

from compas_tna.rhino import FormArtist
from compas_tna.rhino import DiagramHelper

HERE = os.path.abspath(os.path.dirname(__file__))

try:
    import rhinoscriptsyntax as rs
except ImportError:
    pass


__all__ = ['FormActions']


# constrain to curve
# update constraints
# move on constraint
# update boundary conditions?
# update feet
# relax openings (control sag)
# parallelise to self


class FormActions(object):

    def form_update_attributes(self):
        compas_rhino.update_settings(self.form.attributes)

    def form_update_boundaries(self):
        self.form.update_boundaries()

    # --------------------------------------------------------------------------

    def form_from_obj(self):
        path = compas_rhino.select_file(folder=HERE, filter='OBJ files (*.obj)|*.obj||')
        if not path:
            return
        self.form = FormDiagram.from_obj(path)
        guids = compas_rhino.select_curves()
        if guids:
            for guid in guids:
                keys = DiagramHelper.identify_vertices_on_curve(self.form, guid)
                self.form.set_vertices_attribute('constraint', str(guid), keys)
                self.form.set_vertices_attribute('is_anchor', True, keys)
            self.form.update_boundaries()
        self.form.draw(layer=self.settings['form.layer'])

    def form_to_obj(self):
        raise NotImplementedError

    def form_from_mesh(self):
        guid = compas_rhino.select_mesh()
        if not guid:
            return
        self.form = FormDiagram.from_rhinomesh(guid)
        guids = compas_rhino.select_curves()
        if guids:
            for guid in guids:
                keys = DiagramHelper.identify_vertices_on_curve(self.form, guid)
                self.form.set_vertices_attribute('constraint', str(guid), keys)
                self.form.set_vertices_attribute('is_anchor', True, keys)
            self.form.update_boundaries()
        self.form.draw(layer=self.settings['form.layer'])

    def form_to_mesh(self):
        artist = FormArtist(self.form, layer=self.settings['form.layer'])
        artist.draw_faces(join_faces=True)
        artist.redraw()

    # --------------------------------------------------------------------------

    def form_update_vertex_attr(self):
        keys = DiagramHelper.select_vertices(self.form)
        if not keys:
            return
        if DiagramHelper.update_vertex_attributes(self.form, keys):
            self.form.draw(layer=self.settings['form.layer'])

    def form_update_edge_attr(self):
        keys = DiagramHelper.select_edges(self.form)
        if not keys:
            return
        if DiagramHelper.update_edge_attributes(self.form, keys):
            self.form.draw(layer=self.settings['form.layer'])

    def form_update_face_attr(self):
        keys = DiagramHelper.select_faces(self.form)
        if not keys:
            return
        if DiagramHelper.update_face_attributes(self.form, keys):
            self.form.draw(layer=self.settings['form.layer'])

    # --------------------------------------------------------------------------

    def form_move(self):
        DiagramHelper.move(self.form)
        self.form.draw(layer=self.settings['form.layer'])

    def form_move_vertex(self):
        key = DiagramHelper.select_vertex(self.form)
        if key is None:
            return
        DiagramHelper.move_vertex(self.form, key)
        self.form.draw(layer=self.settings['form.layer'])

    def form_move_vertices(self):
        keys = DiagramHelper.select_vertices(self.form)
        if not keys:
            return
        DiagramHelper.move_vertices(self.form, keys)
        self.form.draw(layer=self.settings['form.layer'])

    # --------------------------------------------------------------------------

    # smooth inner
    # smooth unsupported edges
    # smooth outer
    # smooth != relax

    def form_smooth_area(self):
        fixed = list(self.form.vertices_where({'is_anchor': True}))
        fixed += list(self.form.vertices_where({'is_fixed': True}))
        mesh_smooth_area(self.form, fixed=list(set(fixed)), kmax=50)
        self.form.draw(layer=self.settings['form.layer'])

    def form_smooth_centroid(self):
        fixed = list(self.form.vertices_where({'is_anchor': True}))
        fixed += list(self.form.vertices_where({'is_fixed': True}))
        mesh_smooth_centroid(self.form, fixed=list(set(fixed)), kmax=50)
        self.form.draw(layer=self.settings['form.layer'])

    # --------------------------------------------------------------------------

    def form_select_vertices(self):
        modes = ["anchors", "external", "fixed", "openings", "curves"]
        mode = rs.GetString("Selection mode", modes[0], modes)

        if mode == "anchors":
            DiagramHelper.select_vertices_where(self.form, list(self.form.vertices_where({'is_anchor': True})))

        elif mode == "external":
            DiagramHelper.select_vertices_where(self.form, list(self.form.vertices_where({'is_external': True})))

        elif mode == "fixed":
            DiagramHelper.select_vertices_where(self.form, list(self.form.vertices_where({'is_fixed': True})))

        elif mode == "openings":
            artist = FormArtist(self.form, layer=self.settings['form.layer'])
            artist.clear_vertexlabels()
            artist.clear_edgelabels()
            artist.clear_facelabels()
            artist.draw_facelabels(
                text={fkey: str(fkey) for fkey in self.form.faces_where({'is_loaded': False})}
            )
            artist.redraw()

            fkeys = DiagramHelper.select_faces(self.form)

            if not fkeys:
                artist.clear_facelabels()
                artist.redraw()
                return

            keys = []
            for fkey in fkeys:
                for key in self.form.face_vertices(fkey):
                    if not self.form.get_vertex_attributes(key, 'is_anchor') and not self.form.get_vertex_attribute(key, 'is_external'):
                        keys.append(key)

            DiagramHelper.select_vertices_where(self.form, keys)
            artist.clear_facelabels()
            artist.redraw()

        elif mode == "curves":
            DiagramHelper.select_vertices_on_curves(self.form)

        else:
            raise NotImplementedError

    def form_select_edges(self):
        modes = ["continuous", "parallel"]
        mode = rs.GetString("Selection mode", modes[0], modes)
        if mode == "continuous":
            DiagramHelper.select_continuous_edges(self.form)
        elif mode == "parallel":
            DiagramHelper.select_parallel_edges(self.form)
        else:
            raise NotImplementedError

    def form_select_faces(self):
        raise NotImplementedError


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
