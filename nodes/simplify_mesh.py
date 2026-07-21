from gen.messages_pb2 import SimplifyMeshInput, SimplifyMeshOutput, Mesh
from gen.axiom_context import AxiomContext
from nodes._mesh import load_trimesh, encode


def simplify_mesh(ax: AxiomContext, input: SimplifyMeshInput) -> SimplifyMeshOutput:
    """Decimate a mesh to (approximately) a target face count using
    quadric-error-metric simplification (the `fast-simplification` backend),
    preserving overall shape while reducing triangle count.
    """
    mesh = load_trimesh(input.mesh)
    original_faces = len(mesh.faces)
    target = input.target_face_count
    if target <= 0:
        raise ValueError("target_face_count must be > 0")
    target = max(4, min(target, original_faces))
    simplified = mesh.simplify_quadric_decimation(face_count=target)
    out_fmt = input.mesh.format or "STL"
    return SimplifyMeshOutput(
        mesh=Mesh(**encode(simplified, out_fmt)), face_count=len(simplified.faces)
    )
