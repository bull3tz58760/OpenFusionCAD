from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Ax1
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_MakeFace
)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeRevol
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeCircle

def make_rectangle_sketch(width=40, height=30):
    p1 = gp_Pnt(0, 0, 0)
    p2 = gp_Pnt(width, 0, 0)
    p3 = gp_Pnt(width, height, 0)
    p4 = gp_Pnt(0, height, 0)

    e1 = BRepBuilderAPI_MakeEdge(p1, p2).Edge()
    e2 = BRepBuilderAPI_MakeEdge(p2, p3).Edge()
    e3 = BRepBuilderAPI_MakeEdge(p3, p4).Edge()
    e4 = BRepBuilderAPI_MakeEdge(p4, p1).Edge()

    wire = BRepBuilderAPI_MakeWire(e1, e2, e3, e4).Wire()
    return wire

def make_circle_sketch(radius=25):
    circle_edge = BRepBuilderAPI_MakeCircle(gp_Pnt(0, 0, 0), radius).Edge()
    wire = BRepBuilderAPI_MakeWire(circle_edge).Wire()
    return wire

def extrude_sketch(wire, depth=20):
    face = BRepBuilderAPI_MakeFace(wire).Face()
    vector = gp_Vec(0, 0, depth)
    solid = BRepPrimAPI_MakePrism(face, vector).Shape()
    return solid

def revolve_sketch(wire, angle_deg=360):
    face = BRepBuilderAPI_MakeFace(wire).Face()
    axis = gp_Ax1(gp_Pnt(0, 0, 0), gp_Vec(0, 1, 0))  # Revolve around Y axis
    solid = BRepPrimAPI_MakeRevol(face, axis, angle_deg * 3.14159 / 180.0).Shape()
    return solid

from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe
from OCC.Core.gp import gp_Pnt

def make_sweep():
    # Profile: circle in XZ plane at origin
    from OCC.Core.gp import gp_Circ, gp_Ax2, gp_Dir
    circ = gp_Circ(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1)), 5)
    profile_edge = BRepBuilderAPI_MakeEdge(circ).Edge()
    profile_wire = BRepBuilderAPI_MakeWire(profile_edge).Wire()

    # Path: line in Y direction
    p1 = gp_Pnt(0, 0, 0)
    p2 = gp_Pnt(0, 100, 0)
    path_edge = BRepBuilderAPI_MakeEdge(p1, p2).Edge()
    path_wire = BRepBuilderAPI_MakeWire(path_edge).Wire()

    # Sweep operation
    pipe = BRepOffsetAPI_MakePipe(path_wire, profile_wire).Shape()
    return pipe