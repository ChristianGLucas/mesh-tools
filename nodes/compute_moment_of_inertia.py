from gen.messages_pb2 import Mesh, MomentOfInertiaOutput
from gen.axiom_context import AxiomContext
from nodes._mesh import load_trimesh, point3


def compute_moment_of_inertia(ax: AxiomContext, input: Mesh) -> MomentOfInertiaOutput:
    """Compute the 3x3 inertia tensor about the center of mass, for a
    unit-density solid. Only physically meaningful when the mesh is
    watertight (reported via `is_watertight`).
    """
    mesh = load_trimesh(input)
    tensor = mesh.moment_inertia.reshape(-1).tolist()
    return MomentOfInertiaOutput(
        tensor=tensor,
        center_of_mass=point3(*mesh.center_mass),
        is_watertight=bool(mesh.is_watertight),
    )
