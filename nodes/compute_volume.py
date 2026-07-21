from gen.messages_pb2 import Mesh, VolumeOutput
from gen.axiom_context import AxiomContext
from nodes._mesh import load_trimesh


def compute_volume(ax: AxiomContext, input: Mesh) -> VolumeOutput:
    """Compute the signed enclosed volume of a mesh. Only physically
    meaningful when the mesh is watertight (a closed 2-manifold) — that
    condition is reported alongside the value so callers can distinguish a
    real volume from an ill-defined one.
    """
    mesh = load_trimesh(input)
    return VolumeOutput(volume=float(mesh.volume), is_watertight=bool(mesh.is_watertight))
