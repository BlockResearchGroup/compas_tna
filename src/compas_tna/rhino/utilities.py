# -*- coding: utf-8 -*-
# @Date         : 2016-03-21 09:50:20
# @Author       : Tom Van Mele (vanmelet@ethz.ch)
# @Version      : $Id$
# @License      : Apache License, Version 2.0
# @Contributors : ...
# @Copyright    : Block Research Group

import rhinoscriptsyntax as rs
import compas_rhino.utilities as rhino


def get_formdiagram_input(message='Select input objects.'):
    """"""
    points = []
    lines = []
    polylines = []
    guids = rs.GetObjects(message, filter=rs.filter.curve | rs.filter.point)
    if not guids:
        return points, lines, polylines
    for guid in guids:
        if rs.IsPoint(guid):
            p = rs.PointCoordinates(guid)
            if p:
                pos   = map(float, p)
                name  = rs.ObjectName(guid)
                color = rs.ObjectColor(guid)
                color = color.R, color.G, color.B
                attr  = rhino.get_attributes_from_name(name)
                points.append({
                    'pos'   : pos,
                    'name'  : name,
                    'color' : color,
                    'attr'  : attr,
                })
        elif rs.IsLine(guid):
            if 1 == rs.CurveDegree(guid):
                sp = map(float, rs.CurveStartPoint(guid))
                ep = map(float, rs.CurveEndPoint(guid))
                if sp and ep:
                    color = rs.ObjectColor(guid)
                    color = color.R, color.G, color.B
                    name  = rs.ObjectName(guid)
                    attr  = rhino.get_attributes_from_name(name)
                    lines.append({
                        'start' : sp,
                        'end'   : ep,
                        'name'  : name,
                        'color' : color,
                        'attr'  : attr,
                    })
        elif rs.IsPolyline(guid):
            if 1 == rs.CurveDegree(guid):
                corners = rs.CurvePoints(guid)
                corners[:] = map(list, corners)
                color = rs.ObjectColor(guid)
                color = color.R, color.G, color.B
                name  = rs.ObjectName(guid)
                attr  = rhino.get_attributes_from_name(name)
                polylines.append({
                    'points' : corners,
                    'name'   : name,
                    'color'  : color,
                    'attr'   : attr,
                })
        elif rs.IsCurve(guid):
            sp = map(float, rs.CurveStartPoint(guid))
            ep = map(float, rs.CurveEndPoint(guid))
            if sp and ep:
                color = rs.ObjectColor(guid)
                color = color.R, color.G, color.B
                name  = rs.ObjectName(guid)
                attr  = rhino.get_attributes_from_name(name)
                lines.append({
                    'start' : sp,
                    'end'   : ep,
                    'name'  : name,
                    'color' : color,
                    'attr'  : attr,
                })
        else:
            pass
    return points, lines, polylines
