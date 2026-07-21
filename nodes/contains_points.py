from gen.messages_pb2 import ContainsPointsInput, ContainsPointsOutput
from gen.axiom_context import AxiomContext
from nodes._mesh import load_trimesh, array_from_point3s, MAX_QUERY_POINTS, MAX_RAY_QUERY_FACES


def contains_points(ax: AxiomContext, input: ContainsPointsInput) -> ContainsPointsOutput:
    """Test whether each of a set of points lies inside a mesh's enclosed
    volume, via trimesh's ray-casting point-in-mesh test. Only meaningful for
    a watertight mesh (reported via `is_watertight`, returned regardless).
    Bounded in point count and mesh face count (see nodes/_mesh.py).
    """
    mesh = load_trimesh(input.mesh)
    if len(mesh.faces) > MAX_RAY_QUERY_FACES:
        raise ValueError(
            f"mesh has too many faces for containment queries: {len(mesh.faces)} (max {MAX_RAY_QUERY_FACES})"
        )
    points = array_from_point3s(input.points)
    if len(points) == 0:
        raise ValueError("at least one point is required")
    if len(points) > MAX_QUERY_POINTS:
        raise ValueError(f"too many points: {len(points)} (max {MAX_QUERY_POINTS})")

    inside = mesh.contains(points)
    return ContainsPointsOutput(
        inside=[bool(i) for i in inside], is_watertight=bool(mesh.is_watertight)
    )
