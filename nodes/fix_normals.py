from gen.messages_pb2 import Mesh, FixNormalsOutput
from gen.axiom_context import AxiomContext
from nodes._mesh import load_trimesh, encode
import trimesh.repair as repair


def fix_normals(ax: AxiomContext, input: Mesh) -> FixNormalsOutput:
    """Repair face winding so normals point consistently outward, using
    trimesh's adjacency-graph-based winding repair (trimesh.repair.fix_normals).
    Returns the repaired mesh and whether winding is now consistent.
    """
    mesh = load_trimesh(input)
    repair.fix_normals(mesh)
    out_fmt = input.format or "STL"
    return FixNormalsOutput(
        mesh=Mesh(**encode(mesh, out_fmt)),
        is_winding_consistent=bool(mesh.is_winding_consistent),
    )
