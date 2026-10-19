"""STL analysis for the WatchPi enclosure revisions.
Usage: python3 -I stl_analysis.py r1.stl r2.stl r3.stl r4.stl r5.stl
Outputs: mesh integrity, volume, area, bounding box, layer-height check,
facet-based chord deviation, overhang (support-needing) area in 3 orientations,
and an r4-vs-r5 Boolean difference.
"""
import sys, json, numpy as np, trimesh

LAYER = 0.16
ANGLES = [45, 50, 60]  # overhang thresholds from vertical (deg); Cura's 'Support Overhang Angle'


def overhang_area(mesh, angle_deg, plate_tol=0.05):
    """Area of downward faces steeper than threshold, excluding faces resting on the build plate."""
    n = mesh.face_normals
    a = mesh.area_faces
    zmin = mesh.bounds[0, 2]
    fz = mesh.triangles[:, :, 2].mean(axis=1)
    # face needs support if its normal points down more than cos(angle) and it's not on the plate
    needs = (n[:, 2] < -np.cos(np.radians(angle_deg))) & (fz > zmin + plate_tol)
    return float(a[needs].sum())


def chord_deviation(mesh):
    """Estimate tessellation sagitta on the largest circular profile: R*(1-cos(pi/N))."""
    v = mesh.vertices
    c = (mesh.bounds[0, :2] + mesh.bounds[1, :2]) / 2
    for _ in range(3):  # refine centre with a Kasa circle fit on the outermost vertices
        r = np.linalg.norm(v[:, :2] - c, axis=1)
        sel = v[r > np.percentile(r, 80), :2]
        A = np.c_[2 * sel, np.ones(len(sel))]
        sol = np.linalg.lstsq(A, (sel ** 2).sum(1), rcond=None)[0]
        c = sol[:2]
    r = np.linalg.norm(v[:, :2] - c, axis=1)
    R = np.median(r[r > np.percentile(r, 90)])
    ring = v[np.abs(r - R) < 0.05]
    ang = np.unique(np.round(np.degrees(np.arctan2(ring[:, 1] - c[1], ring[:, 0] - c[0])), 2))
    N = len(ang)
    if N < 8:
        return None
    return {"outer_radius_mm": round(float(R), 3), "segments": int(N),
            "sagitta_mm": round(float(R * (1 - np.cos(np.pi / N))), 4)}


def orientations(mesh):
    out = {}
    m = mesh.copy(); out["as_exported"] = m
    m = mesh.copy(); m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])); out["flipped_180"] = m
    m = mesh.copy(); m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])); out["on_side_90"] = m
    return out


def analyse(path):
    m = trimesh.load_mesh(path, force="mesh")
    res = {"file": path, "faces": int(len(m.faces)), "watertight": bool(m.is_watertight),
           "winding_consistent": bool(m.is_winding_consistent), "euler": int(m.euler_number),
           "bodies": int(len(m.split(only_watertight=False))),
           "volume_mm3": round(float(m.volume), 1), "area_mm2": round(float(m.area), 1)}
    ext = m.extents
    res["bbox_mm"] = [round(float(e), 2) for e in ext]
    res["z_height_mm"] = round(float(ext[2]), 2)
    res["layers_if_uniform_0.16"] = round(float(ext[2] / LAYER), 1)
    res["chord"] = chord_deviation(m)
    res["overhang_mm2"] = {k: {a: round(overhang_area(mm, a), 1) for a in ANGLES}
                           for k, mm in orientations(m).items()}
    return m, res


if __name__ == "__main__":
    meshes, rows = [], []
    for p in sys.argv[1:]:
        m, r = analyse(p); meshes.append(m); rows.append(r)
        print(json.dumps(r, indent=1))
    # r4 -> r5 volume changes are located with scripts/slicediff.py (cross-section differences).
