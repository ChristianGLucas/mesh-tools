from gen.messages_pb2 import Mesh, SurfaceAreaOutput
from gen.axiom_context import AxiomContext
from nodes._mesh import load_trimesh


def compute_surface_area(ax: AxiomContext, input: Mesh) -> SurfaceAreaOutput:
    """Compute the total surface area of a mesh (sum of triangle areas).
    Well-defined for any mesh, watertight or not.
    """
    mesh = load_trimesh(input)
    return SurfaceAreaOutput(area=float(mesh.area))
