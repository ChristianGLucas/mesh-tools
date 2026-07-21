from gen.messages_pb2 import Mesh, CenterOfMassOutput
from gen.axiom_context import AxiomContext
from nodes._mesh import load_trimesh, point3


def compute_center_of_mass(ax: AxiomContext, input: Mesh) -> CenterOfMassOutput:
    """Compute the center of mass of a mesh, assuming uniform density. Exact
    for a watertight mesh; falls back to trimesh's vertex-mean approximation
    otherwise (reported via `is_watertight`).
    """
    mesh = load_trimesh(input)
    cm = mesh.center_mass
    return CenterOfMassOutput(center_of_mass=point3(*cm), is_watertight=bool(mesh.is_watertight))
