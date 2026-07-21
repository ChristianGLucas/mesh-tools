"""Shared trimesh helpers: canonical `Mesh` message <-> a decoded trimesh.Trimesh.

Every node is a thin wrapper around trimesh (MIT). This module is the single
place that knows how the `Mesh` envelope's bytes/URL are decoded, how a
transformed trimesh.Trimesh is re-encoded back into a `Mesh`, and the size/
count caps that bound cost on untrusted input.

LICENSE NOTE — the rtree bypass
--------------------------------
trimesh's default ray-triangle broad-phase index (`Trimesh.triangles_tree`,
used by `mesh.ray.*`, `mesh.contains()`, and `trimesh.sample.volume_mesh`)
calls `trimesh.util.bounds_tree()`, which unconditionally imports `rtree`.
`rtree` wraps `libspatialindex`, distributed under LGPL-2.1 — a copyleft
license this package's selection gate rejects, so `rtree` is deliberately
NOT a dependency (see requirements.txt).

Instead, `_install_brute_bounds_tree()` monkeypatches
`trimesh.triangles.bounds_tree` with `_BruteBoundsTree`, a pure-numpy
broad-phase substitute implementing the two methods trimesh's own
`ray_triangle_candidates()` needs (`.bounds`, `.intersection(box)`) via a
linear AABB-overlap scan instead of an R-tree. This only changes which
triangles are considered *candidates* for a ray/point query — every actual
geometric computation (ray-triangle intersection, winding, inside/outside
parity counting, hit deduplication) remains 100% trimesh's own code. For the
face counts this package accepts (bounded below), the linear scan is fast
and the substitution is exact, not an approximation.

We also do not depend on `shapely` (trimesh's `Trimesh.slice_plane()` /
cross-section path) because `shapely` links `GEOS`, also LGPL-2.1 — so no
plane-slicing node is exposed by this package (see the package retrospective
for what else was left out and why).
"""
from __future__ import annotations

import io
import ipaddress
import socket
import urllib.request
from urllib.parse import urlparse

import numpy as np
import trimesh
import trimesh.triangles as _triangles_mod

# ---------------------------------------------------------------------------
# rtree-free broad-phase ray/point-containment index (see module docstring).
# ---------------------------------------------------------------------------


class _BruteBoundsTree:
    """Pure-numpy stand-in for `rtree.Index`, implementing only the interface
    `trimesh.ray.ray_triangle.ray_triangle_candidates()` calls."""

    def __init__(self, triangle_bounds: np.ndarray):
        # triangle_bounds: (n, 6) = [minx, miny, minz, maxx, maxy, maxz] per triangle.
        self._min = triangle_bounds[:, :3]
        self._max = triangle_bounds[:, 3:]
        self.bounds = np.concatenate([self._min.min(axis=0), self._max.max(axis=0)])

    def intersection(self, bounds):
        bounds = np.asarray(bounds, dtype=np.float64)
        qmin, qmax = bounds[:3], bounds[3:]
        ok = np.all(self._min <= qmax, axis=1) & np.all(self._max >= qmin, axis=1)
        return np.nonzero(ok)[0]


def _brute_bounds_tree(triangles) -> _BruteBoundsTree:
    triangles = np.asanyarray(triangles, dtype=np.float64)
    triangle_bounds = np.column_stack((triangles.min(axis=1), triangles.max(axis=1)))
    return _BruteBoundsTree(triangle_bounds)


def _install_brute_bounds_tree() -> None:
    if getattr(_triangles_mod, "bounds_tree", None) is not _brute_bounds_tree:
        _triangles_mod.bounds_tree = _brute_bounds_tree


_install_brute_bounds_tree()

# ---------------------------------------------------------------------------
# Format handling
# ---------------------------------------------------------------------------

SUPPORTED_FORMATS = ("STL", "OBJ", "PLY", "GLB")


def normalize_format(fmt: str) -> str:
    f = (fmt or "").strip().upper()
    if f == "GLTF":
        f = "GLB"
    return f


# ---------------------------------------------------------------------------
# Size/count caps — bound cost on untrusted input before we parse/process it.
# ---------------------------------------------------------------------------

MAX_MESH_BYTES = 25 * 1024 * 1024  # 25 MiB raw file
MAX_FETCH_BYTES = MAX_MESH_BYTES
MAX_VERTICES = 500_000
MAX_FACES = 1_000_000
# Ray/contains broad-phase is O(rays * faces) in the worst case (see
# _BruteBoundsTree above) — bound both dimensions tighter for those nodes.
MAX_RAY_QUERY_FACES = 100_000
MAX_RAYS = 5_000
MAX_QUERY_POINTS = 5_000
MAX_SAMPLE_COUNT = 100_000


def _check_mesh_size(raw: bytes) -> None:
    if len(raw) > MAX_MESH_BYTES:
        raise ValueError(f"mesh data too large: {len(raw)} bytes (max {MAX_MESH_BYTES})")


def _check_mesh_counts(mesh: "trimesh.Trimesh") -> None:
    if len(mesh.vertices) > MAX_VERTICES:
        raise ValueError(f"mesh has too many vertices: {len(mesh.vertices)} (max {MAX_VERTICES})")
    if len(mesh.faces) > MAX_FACES:
        raise ValueError(f"mesh has too many faces: {len(mesh.faces)} (max {MAX_FACES})")


# ---------------------------------------------------------------------------
# URL fetch — scheme-restricted and SSRF-guarded at dial time.
# ---------------------------------------------------------------------------


def _guard_not_private(host: str) -> None:
    """Resolve `host` and reject if any resolved address is private/loopback/
    link-local/reserved. Best-effort (DNS can still rebind between this check
    and connect), but blocks the overwhelmingly common SSRF pattern of a
    caller-supplied URL pointing at localhost/cloud-metadata/internal IPs."""
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise ValueError(f"could not resolve host: {host}") from exc
    for info in infos:
        addr = info[4][0]
        ip = ipaddress.ip_address(addr)
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
            or ip.is_unspecified
        ):
            raise ValueError(f"refusing to fetch from non-public address: {host} -> {addr}")


def _fetch(url: str) -> bytes:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"unsupported URL scheme: {parsed.scheme!r} (only http/https)")
    if not parsed.hostname:
        raise ValueError("URL has no host")
    _guard_not_private(parsed.hostname)
    req = urllib.request.Request(url, headers={"User-Agent": "axiom-mesh-tools/0.1"})
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 (scheme+SSRF-guarded above)
        raw = resp.read(MAX_MESH_BYTES + 1)
    _check_mesh_size(raw)
    return raw


# ---------------------------------------------------------------------------
# Mesh message <-> trimesh.Trimesh
# ---------------------------------------------------------------------------


def load_trimesh(mesh_msg) -> "trimesh.Trimesh":
    """Resolve a canonical `Mesh` message into a decoded, size-bounded
    trimesh.Trimesh. Uses inline `data` when present; otherwise fetches
    `url`. Raises ValueError on missing/oversized/unparseable input."""
    raw = bytes(mesh_msg.data)
    if not raw:
        if not mesh_msg.url:
            raise ValueError("Mesh has neither `data` nor `url`")
        raw = _fetch(mesh_msg.url)
    _check_mesh_size(raw)

    fmt = normalize_format(mesh_msg.format)
    if not fmt:
        raise ValueError("Mesh.format is required (one of STL, OBJ, PLY, GLB)")
    if fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"unsupported format {fmt!r} (expected one of {SUPPORTED_FORMATS})")

    try:
        # process=True (trimesh's default) welds coincident vertices, drops
        # degenerate/duplicate faces, etc. This is not optional cleanup we're
        # opting into — STL in particular has no shared-vertex topology at
        # all (every triangle stores 3 independent vertices), so without
        # welding, watertightness/Euler number/body-count/booleans are
        # meaningless regardless of format. This is what "parse this mesh
        # file" means for any of the four supported formats.
        loaded = trimesh.load(io.BytesIO(raw), file_type=fmt.lower(), process=True)
    except Exception as exc:  # noqa: BLE001 — normalize any parser failure
        raise ValueError(f"failed to parse mesh as {fmt}: {exc}") from exc

    if isinstance(loaded, trimesh.Scene):
        geoms = [g for g in loaded.geometry.values() if isinstance(g, trimesh.Trimesh)]
        if not geoms:
            raise ValueError(f"{fmt} file contains no triangle mesh geometry")
        mesh = geoms[0] if len(geoms) == 1 else trimesh.util.concatenate(geoms)
    elif isinstance(loaded, trimesh.Trimesh):
        mesh = loaded
    else:
        raise ValueError(f"{fmt} file did not decode to a triangle mesh")

    if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        raise ValueError("mesh has no vertices/faces")

    _check_mesh_counts(mesh)
    return mesh


def encode(mesh: "trimesh.Trimesh", fmt: str) -> dict:
    """Encode a trimesh.Trimesh into canonical `Mesh` field values.

    Returns a dict of keyword arguments a node splats into `Mesh(**...)` —
    keeping the message construction in the node body is what `axiom
    validate` checks for.
    """
    out_fmt = normalize_format(fmt)
    if out_fmt not in SUPPORTED_FORMATS:
        raise ValueError(f"unsupported target format {fmt!r} (expected one of {SUPPORTED_FORMATS})")
    data = mesh.export(file_type=out_fmt.lower())
    if isinstance(data, str):
        data = data.encode("utf-8")
    return {
        "data": data,
        "format": out_fmt,
        "vertex_count": len(mesh.vertices),
        "face_count": len(mesh.faces),
    }


# ---------------------------------------------------------------------------
# Point3 <-> numpy
# ---------------------------------------------------------------------------


def point3(x: float, y: float, z: float):
    from gen.messages_pb2 import Point3

    return Point3(x=float(x), y=float(y), z=float(z))


def point3_from_array(arr) -> list:
    from gen.messages_pb2 import Point3

    return [Point3(x=float(p[0]), y=float(p[1]), z=float(p[2])) for p in arr]


def array_from_point3s(points) -> np.ndarray:
    if len(points) == 0:
        return np.zeros((0, 3), dtype=np.float64)
    return np.array([[p.x, p.y, p.z] for p in points], dtype=np.float64)
