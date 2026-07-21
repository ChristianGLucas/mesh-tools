from gen.messages_pb2 import Mesh, ConvexHullOutput
from gen.axiom_context import AxiomContext
from nodes._mesh import load_trimesh, encode


def compute_convex_hull(ax: AxiomContext, input: Mesh) -> ConvexHullOutput:
    """Compute the convex hull of a mesh's vertices, returned as a new
    watertight mesh (via scipy's Qhull-backed convex_hull), along with the
    hull's own volume and surface area.
    """
    mesh = load_trimesh(input)
    hull = mesh.convex_hull
    out_fmt = input.format or "STL"
    return ConvexHullOutput(
        hull=Mesh(**encode(hull, out_fmt)), volume=float(hull.volume), area=float(hull.area)
    )
