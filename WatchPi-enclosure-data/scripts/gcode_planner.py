"""Per-feature time/filament/path breakdown of slicer G-code with a Marlin-style
look-ahead planner (classic jerk junctions, trapezoidal accel, forward/backward passes).
Usage: python3 -I gcode_planner.py --jerk 8 --accel 2500 file1.gcode [file2 ...]
Feature = the active ';TYPE:' label (PrusaSlicer or Cura). Moves without extrusion = TRAVEL.
"""
import sys, math, json, argparse
from collections import defaultdict


def plan(moves, jerk, amax):
    """moves: list of dicts with d, v, u (unit vec), a, feat. Returns per-move times."""
    n = len(moves)
    vj = [0.0] * (n + 1)  # junction speeds; vj[i] = speed at start of move i
    for i in range(1, n):
        p, q = moves[i - 1], moves[i]
        lim = min(p["v"], q["v"])
        for k in range(3):
            du = abs(p["u"][k] - q["u"][k])
            if du > 1e-9:
                lim = min(lim, jerk[k] / du)
        vj[i] = lim
    vj[0] = 0.0; vj[n] = 0.0
    # backward pass
    for i in range(n - 1, -1, -1):
        m = moves[i]
        vj[i] = min(vj[i], math.sqrt(vj[i + 1] ** 2 + 2 * m["a"] * m["d"]))
    # forward pass
    for i in range(n):
        m = moves[i]
        vj[i + 1] = min(vj[i + 1], math.sqrt(vj[i] ** 2 + 2 * m["a"] * m["d"]))
    times = []
    for i, m in enumerate(moves):
        v0, v1, vc, a, d = vj[i], vj[i + 1], m["v"], m["a"], m["d"]
        da = (vc * vc - v0 * v0) / (2 * a); dd = (vc * vc - v1 * v1) / (2 * a)
        if da + dd <= d:
            t = (vc - v0) / a + (vc - v1) / a + (d - da - dd) / vc
        else:
            vp2 = (2 * a * d + v0 * v0 + v1 * v1) / 2
            vp = math.sqrt(max(vp2, max(v0, v1) ** 2))
            t = (vp - v0) / a + (vp - v1) / a
        times.append(t)
    return times


def parse(path, jerk=(8, 8, 0.4), accel_default=2500.0, accel_travel=None):
    x = y = z = 0.0; f = 25.0; rel_e = True; acc = accel_default; acc_travel = accel_travel or accel_default
    feat = "START"; moves = []; extra = defaultdict(float); fil = defaultdict(float); path_len = defaultdict(float)
    header = {}
    for line in open(path, errors="ignore"):
        if line.startswith(";"):
            if line.startswith(";TYPE:"):
                feat = line[6:].strip()
            elif "=" in line and line.startswith("; ") and len(header) < 400:
                k, v = line[2:].split("=", 1); header[k.strip()] = v.strip()
            continue
        code = line.split(";")[0].split()
        if not code:
            continue
        g = code[0]
        if g == "M83": rel_e = True
        elif g == "M82": rel_e = False
        elif g == "M204":
            for t in code[1:]:
                if t[0] in "SP": acc = float(t[1:])
                if t[0] == "T": acc_travel = float(t[1:])
        elif g in ("G0", "G1"):
            nx, ny, nz, de, hasE = x, y, z, 0.0, False
            for t in code[1:]:
                c, v = t[0], t[1:]
                if c == "X": nx = float(v)
                elif c == "Y": ny = float(v)
                elif c == "Z": nz = float(v)
                elif c == "F": f = float(v) / 60
                elif c == "E": de = float(v); hasE = True
            dx, dy, dz = nx - x, ny - y, nz - z
            d = math.sqrt(dx * dx + dy * dy + dz * dz)
            if d > 1e-6:
                key = feat if de > 0 else "Travel"
                moves.append({"d": d, "v": f, "u": (dx / d, dy / d, dz / d),
                              "a": (acc if de > 0 else acc_travel), "feat": key})
                path_len[key] += d
                if de > 0: fil[key] += de
            elif hasE:  # retract / unretract in place
                extra["Retract/unretract"] += abs(de) / max(f, 1e-6)
            x, y, z = nx, ny, nz
        elif g == "G4":
            for t in code[1:]:
                if t[0] == "S": extra["Dwell"] += float(t[1:])
                if t[0] == "P": extra["Dwell"] += float(t[1:]) / 1000
    times = plan(moves, jerk, accel_default)
    tf = defaultdict(float)
    for m, t in zip(moves, times):
        tf[m["feat"]] += t
    for k, v in extra.items():
        tf[k] += v
    tot = sum(tf.values())
    rows = {k: {"time_min": round(tf[k] / 60, 2), "time_pct": round(100 * tf[k] / tot, 1),
                "filament_m": round(fil.get(k, 0) / 1000, 3), "path_m": round(path_len.get(k, 0) / 1000, 2)} for k in tf}
    return {"file": path, "planner_total_min": round(tot / 60, 2),
            "slicer_total": header.get("estimated printing time (normal mode)"),
            "slicer_filament_mm": header.get("filament used [mm]"), "features": rows}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--jerk", type=float, default=8.0)
    ap.add_argument("--accel", type=float, default=2500.0)
    ap.add_argument("files", nargs="+")
    a = ap.parse_args()
    out = [parse(p, jerk=(a.jerk, a.jerk, 0.4), accel_default=a.accel) for p in a.files]
    print(json.dumps(out, indent=1))
