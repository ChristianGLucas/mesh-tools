import trimesh.sample as sample

from gen.messages_pb2 import SamplePointsInput, SurfacePointsOutput
from gen.axiom_context import AxiomContext
from nodes._mesh import load_trimesh, point3_from_array


def sample_surface_points(ax: AxiomContext, input: SamplePointsInput) -> SurfacePointsOutput:
    """Sample `count` points uniformly at random (by triangle area) from a
    mesh's surface, via trimesh.sample.sample_surface. Deterministic for a
    given (mesh, count, seed). No count cap — area-weighted surface
    sampling is linear cost, unlike the ray-casting nodes (see
    sample_volume_points, contains_points), which do bound their inputs.
    """
    mesh = load_trimesh(input.mesh)
    if input.count <= 0:
        raise ValueError("count must be > 0")
    points, face_indices = sample.sample_surface(mesh, input.count, seed=int(input.seed))
    return SurfacePointsOutput(
        points=point3_from_array(points), face_indices=[int(i) for i in face_indices]
    )
