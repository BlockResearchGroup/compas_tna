from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas_rhino
import compas_tna

from compas.utilities import i2rgb

from compas_tna.diagrams import ThrustDiagram


__author__    = ['Tom Van Mele', ]
__copyright__ = 'Copyright 2014 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'vanmelet@ethz.ch'


__all__ = ['RhinoThrustDiagram', ]


class RhinoThrustDiagram(ThrustDiagram):

    def __init__(self):
        super(RhinoThrustDiagram, self).__init__()
        self.attributes.update({
            'layer': 'ThrustDiagram',
        })

    def draw(self):
        name = '{0}.faces'.format(self.name)
        key_index = dict((k, i) for i, k in self.vertices_enum())
        xyz = self.xyz()
        faces = []
        colors = []
        interpolation = []
        for fkey, vertices in self.face.items():
            if self.dual.vertex[fkey]['is_unloaded']:
                continue
            if vertices[0] == vertices[-1]:
                face = vertices[:-1]
            else:
                face = vertices[:]
            v = len(face)
            if v < 3:
                print 'Degenerate face: {0}'.format(fkey)
            if v == 3:
                face.append(face[-1])
                faces.append([key_index[key] for key in face])
            elif v == 4:
                faces.append([key_index[key] for key in face])
            else:
                c = len(xyz)
                xyz.append(self.face_centroid(fkey))
                for i in range(-1, len(face) - 1):
                    key = face[i]
                    nbr = face[i + 1]
                    temp = [c, key_index[key], key_index[nbr], key_index[nbr]]
                    faces.append(temp)
                interpolation.append([key_index[key] for key in face])
        if not xyz or not faces:
            return
        compas_rhino.xdraw_mesh(xyz,
                         faces,
                         colors,
                         name,
                         layer=self.layer,
                         clear=True,
                         redraw=True)
        self.interpolation = interpolation

    # --------------------------------------------------------------------------
    # coloring
    # --------------------------------------------------------------------------

    # def color_thrustdiagram(thrustdiagram, key_value, level=0.0, i2color=i2rgb):
    #     key_index = dict((k, i) for i, k in thrustdiagram.vertices_enum())
    #     sorted_by_val = sorted(key_value.items(), key=lambda x: x[1])
    #     kmin, vmin = sorted_by_val[0]
    #     kmax, vmax = sorted_by_val[-1]
    #     vrange = (1 - level) * (vmax - vmin)
    #     if not vrange:
    #         colors = [(255, 255, 255)] * len(thrustdiagram.vertices())
    #     else:
    #         colors = [None] * len(thrustdiagram.vertices())
    #         for key, value in key_value.items():
    #             index = key_index[key]
    #             value = (value - vmin) / vrange
    #             value = min(value, 1.0)
    #             value = max(value, 0.0)
    #             colors[index] = i2color(value)
    #     for indices in thrustdiagram.interpolation:
    #         i     = float(len(indices))
    #         rgbs  = [colors[index] for index in indices]
    #         color = [sum(component) / i for component in zip(*rgbs)]
    #         colors.append(color)
    #     objects = compas_rhino.get_objects('{0}.mesh'.format(thrustdiagram.attributes['name']))
    #     if objects:
    #         compas_rhino.set_mesh_vertex_colors(objects[0], colors)


    # def uncolor_thrustdiagram(thrustdiagram):
    #     objects = compas_rhino.get_objects('{0}.mesh'.format(thrustdiagram.attributes['name']))
    #     if objects:
    #         compas_rhino.set_mesh_vertex_colors(objects[0], None)

    # --------------------------------------------------------------------------
    # display deviations
    # --------------------------------------------------------------------------

    def display_dz(self,
                   display=True,
                   layer=None,
                   clear=False,
                   color_above=None,
                   color_below=None,
                   scale=None):
        objects = compas_rhino.get_objects(name='{0}.deviation.*'.format(self.name))
        compas_rhino.delete_objects(objects)
        if not display:
            return
        scale       = scale or self.scale['deviation']
        color_above = color_above or self.color['deviation:above']
        color_below = color_below or self.color['deviation:below']
        layer       = layer or self.layer
        spheres = []
        for key, attr in self.vertices(True):
            if not attr['dz']:
                continue
            pos    = self.vertex_coordinates(key)
            radius = scale * (attr['dz'] ** 2) **  0.5
            name   = '{0}.deviation.{1}'.format(self.name, key)
            color  = color_above if attr['dz'] > 0 else color_below
            spheres.append({'pos'   : pos,
                            'radius': radius,
                            'name'  : name,
                            'color' : color, })
        compas_rhino.xdraw_spheres(spheres, layer=layer, clear=clear)

    def display_dkern(self,
                      display=True,
                      layer=None,
                      clear=False,
                      color_above=None,
                      color_below=None,
                      scale=None):
        objects = compas_rhino.get_objects(name='{0}.deviation.*'.format(self.name))
        compas_rhino.delete_objects(objects)
        if not display:
            return
        scale       = scale or self.scale['deviation']
        color_above = color_above or self.color['deviation:above']
        color_below = color_below or self.color['deviation:below']
        layer       = layer or self.layer
        spheres = []
        for key, attr in self.vertices(True):
            if not attr['dk']:
                continue
            pos    = self.vertex_coordinates(key)
            radius = scale * (attr['dk']**2)**0.5
            name   = '{0}.deviation.{1}'.format(self.name, key)
            color  = color_above if attr['dk'] > 0 else color_below
            spheres.append({'pos'   : pos,
                            'radius': radius,
                            'name'  : name,
                            'color' : color, })
        compas_rhino.xdraw_spheres(spheres, layer=layer, clear=False)

    def display_dthickness(self,
                           display=True,
                           layer=None,
                           clear=False,
                           color_above=None,
                           color_below=None,
                           scale=None):
        objects = compas_rhino.get_objects(name='{0}.deviation.*'.format(self.name))
        compas_rhino.delete_objects(objects)
        if not display:
            return
        scale       = scale or self.scale['deviation']
        color_above = color_above or self.color['deviation:above']
        color_below = color_below or self.color['deviation:below']
        layer       = layer or self.layer
        spheres = []
        for key, attr in self.vertices(True):
            if not attr['dt']:
                continue
            pos   = (attr['x'], attr['y'], attr['z'])
            name  = '{0}.deviation.{1}'.format(self.name, key)
            color = color_above if attr['dt'] > 0 else color_below
            spheres.append({'pos'   : pos,
                            'radius': scale * (attr['dt']**2)**0.5,
                            'name'  : name,
                            'color' : color, })
        compas_rhino.xdraw_spheres(spheres, layer=layer, clear=False, redraw=False)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
