from gen.messages_pb2 import Mesh, BoundingBoxOutput
from gen.axiom_context import AxiomContext
from nodes._mesh import load_trimesh, point3


def compute_bounding_box(ax: AxiomContext, input: Mesh) -> BoundingBoxOutput:
    """Compute the axis-aligned bounding box of a mesh: min/max corners,
    per-axis extents, and the box's own volume.
    """
    mesh = load_trimesh(input)
    bmin, bmax = mesh.bounds
    extents = mesh.extents
    volume = float(extents[0] * extents[1] * extents[2])
    return BoundingBoxOutput(
        min=point3(*bmin), max=point3(*bmax), extents=point3(*extents), volume=volume
    )
