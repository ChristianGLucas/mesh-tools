import numpy as np

from gen.messages_pb2 import RayIntersectInput, RayIntersectOutput
from gen.axiom_context import AxiomContext
from nodes._mesh import (
    load_trimesh,
    array_from_point3s,
    point3_from_array,
    MAX_RAYS,
    MAX_RAY_QUERY_FACES,
)


def ray_intersect(ax: AxiomContext, input: RayIntersectInput) -> RayIntersectOutput:
    """Cast rays (origin + direction pairs) against a mesh and report every
    intersection point, via trimesh's ray-triangle intersector. A ray may
    produce zero, one, or multiple hits; `ray_hit` reports per-ray whether it
    hit at all. Bounded in ray count and mesh face count since broad-phase
    candidate selection here is a linear scan (see nodes/_mesh.py).
    """
    mesh = load_trimesh(input.mesh)
    if len(mesh.faces) > MAX_RAY_QUERY_FACES:
        raise ValueError(
            f"mesh has too many faces for ray queries: {len(mesh.faces)} (max {MAX_RAY_QUERY_FACES})"
        )
    origins = array_from_point3s(input.origins)
    directions = array_from_point3s(input.directions)
    if len(origins) != len(directions):
        raise ValueError("origins and directions must be the same length")
    if len(origins) == 0:
        raise ValueError("at least one ray (origins/directions) is required")
    if len(origins) > MAX_RAYS:
        raise ValueError(f"too many rays: {len(origins)} (max {MAX_RAYS})")

    locations, index_ray, index_tri = mesh.ray.intersects_location(
        ray_origins=origins, ray_directions=directions
    )
    ray_hit = np.zeros(len(origins), dtype=bool)
    if len(index_ray) > 0:
        ray_hit[np.unique(index_ray)] = True

    return RayIntersectOutput(
        locations=point3_from_array(locations),
        ray_indices=[int(i) for i in index_ray],
        triangle_indices=[int(i) for i in index_tri],
        ray_hit=[bool(h) for h in ray_hit],
    )
