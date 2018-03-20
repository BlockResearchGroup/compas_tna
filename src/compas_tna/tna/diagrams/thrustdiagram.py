# -*- coding: utf-8 -*-
# @Date         : 2016-03-21 09:50:20
# @Author       : Tom Van Mele (vanmelet@ethz.ch)
# @Contributors : ...
# @Version      : $Id$
# @Copyright    : 'Copyright 2014, BLOCK Research Group - ETH Zurich'
# @License      : 'Apache License, Version 2.0'


from compas_tna.formdiagram import FormDiagram


class ThrustDiagram(FormDiagram):
    """"""

    default_vertex_attributes = FormDiagram.default_vertex_attributes.copy()
    default_edge_attributes = FormDiagram.default_edge_attributes.copy()

    default_vertex_attributes.update({
        'rx' : 0.0,
        'ry' : 0.0,
        'rz' : 0.0,
        'dz' : 0.0,
        'dk' : 0.0,
        'dt' : 0.0,
    })
    default_edge_attributes.update({
        'f' : 0.0,
    })

    def __init__(self):
        super(ThrustDiagram, self).__init__()
        self.attributes.update({
            'name'                  : 'ThrustDiagram',
            'color.load:applied'    : (0, 255, 0),
            'color.load:selfweight' : (0, 255, 0),
            'color.force:residual'  : (0, 255, 255),
            'color.force:reaction'  : (255, 0, 0),
            'color.force:axial'     : (53, 53, 53),
            'color.deviation:above' : (255, 0, 0),
            'color.deviation:below' : (0, 0, 255),
            'scale.load:applied'    : 1.0,
            'scale.load:selfweight' : 1.0,
            'scale.force:residual'  : 1.0,
            'scale.force:reaction'  : 0.5,
            'scale.force:axial'     : 0.05,
            'scale.deviation'       : 1.0,
        })

    @property
    def scale(self):
        return dict(
            (key[6:], self.attributes[key])
            for key in self.attributes if key.startswith('scale.')
        )

    @scale.setter
    def scale(self, value):
        try:
            value[0]
            value[1]
            value[1][2]
        except Exception:
            return
        self.attributes['scale.{0}'.format(value[0])] = value[1]

    # --------------------------------------------------------------------------
    # Convenience functions for retrieving attributes of the thrust network.
    # --------------------------------------------------------------------------

    def edge_width(self, u, v, fkey_centroid=None):
        if not fkey_centroid:
            fkey_centroid = self.face_centroid()
        fkey = self.halfedge[u][v]
        if fkey in fkey_centroid:
            c1 = fkey_centroid[fkey]
        else:
            c1 = self.edge_midpoint(u, v)
        fkey = self.halfedge[v][u]
        if fkey in fkey_centroid:
            c2 = fkey_centroid[fkey]
        else:
            c2 = self.edge_midpoint(v, u)
        w = (sum([(c1[_] - c2[_]) ** 2 for _ in range(3)])) ** 0.5
        return w

    def _lump_force(self, key, fkey_centroid):
        force = 0
        nbrs = self.halfedge[key].keys()
        for nbr in nbrs:
            if nbr in self.edge[key]:
                f = self.edge[key][nbr]['f']
            else:
                f = self.edge[nbr][key]['f']
            w = self.edge_width(key, nbr, fkey_centroid)
            force += f / w
        return force / len(nbrs)

    def lump_force(self, key=None):
        fkey_centroid = self.face_centroid()
        if key is None:
            return dict(
                (key, self._lump_force(key, fkey_centroid))
                for key in self.vertices_iter()
            )
        return self._lump_force(key, fkey_centroid)

    def edge_area(self, u, v, fkey_centroid=None):
        w = self.edge_width(u, v, fkey_centroid=fkey_centroid)
        t = (self.vertex[u]['t'] + self.vertex[v]['t']) * 0.5
        area = w * t
        return area

    def _lump_stress(self, key, fkey_centroid):
        s = 0
        nbrs = self.halfedge[key].keys()
        for nbr in nbrs:
            if nbr in self.edge[key]:
                f = self.edge[key][nbr]['f']
            else:
                f = self.edge[nbr][key]['f']
            a = self.edge_area(key, nbr, fkey_centroid)
            if not a:
                a = 1.0
            s += f / a
        return s / len(nbrs)

    def lump_stress(self, key=None):
        fkey_centroid = self.face_centroid()
        if key is None:
            return dict(
                (key, self._lump_stress(key, fkey_centroid))
                for key in self.vertices_iter()
            )
        return self._lump_stress(key, fkey_centroid)

    def minmax_attr_values(self, name='f', return_keys=False):
        key_value = dict(((u, v), attr[name]) for u, v, attr in self.edges(True))
        kmax, vmax = max(key_value.items(), key=lambda x: x[1])
        kmin, vmin = min(key_value.items(), key=lambda x: x[1])
        if return_keys:
            kmin, vmin, kmax, vmax
        return vmin, vmax


# ==============================================================================
# Debugging
# ==============================================================================

if __name__ == '__main__':
    pass
