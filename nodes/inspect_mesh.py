from gen.messages_pb2 import Mesh, InspectMeshOutput
from gen.axiom_context import AxiomContext
from nodes._mesh import load_trimesh, normalize_format, point3


def inspect_mesh(ax: AxiomContext, input: Mesh) -> InspectMeshOutput:
    """Parse a mesh (STL/OBJ/PLY/GLB) and report a structural + topological
    summary: vertex/face counts, axis-aligned bounds and extents, whether it
    is watertight (closed 2-manifold), winding-consistent, its Euler
    characteristic, and its connected-component ("body") count. Doubles as
    the general-purpose validity check — malformed input raises rather than
    returning a partial summary.
    """
    mesh = load_trimesh(input)
    bmin, bmax = mesh.bounds
    extents = mesh.extents
    return InspectMeshOutput(
        format=normalize_format(input.format),
        vertex_count=len(mesh.vertices),
        face_count=len(mesh.faces),
        bounds_min=point3(*bmin),
        bounds_max=point3(*bmax),
        extents=point3(*extents),
        is_watertight=bool(mesh.is_watertight),
        is_winding_consistent=bool(mesh.is_winding_consistent),
        euler_number=int(mesh.euler_number),
        body_count=int(mesh.body_count),
    )
