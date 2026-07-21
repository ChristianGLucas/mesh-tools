from gen.messages_pb2 import BooleanInput, BooleanOutput, Mesh
from gen.axiom_context import AxiomContext
from nodes._mesh import load_trimesh, encode
import trimesh.boolean as boolean


def boolean_union(ax: AxiomContext, input: BooleanInput) -> BooleanOutput:
    """Compute the boolean union (a OR b) of two meshes, via the Apache-2.0
    manifold3d engine (Manifold's exact boolean algorithm). Both inputs
    should be watertight for a well-defined result.
    """
    mesh_a = load_trimesh(input.a)
    mesh_b = load_trimesh(input.b)
    result = boolean.union([mesh_a, mesh_b], engine="manifold")
    out_fmt = input.a.format or "STL"
    return BooleanOutput(
        mesh=Mesh(**encode(result, out_fmt)),
        volume=float(result.volume),
        is_watertight=bool(result.is_watertight),
    )
