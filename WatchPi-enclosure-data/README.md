# WatchPi enclosure – data and analysis

Supporting data for *Iterative Design of a Compact Wearable Enclosure: Overhang Support, Not Enclosure Size, Governs Slicer-Estimated Print Time* (Abhigna Yerramreddikalva).

## Contents

| Folder | What it holds |
|---|---|
| `stl/` | STL meshes of the five enclosure revisions, `r1.stl` … `r5.stl` (exported from CAD; enclosure only). |
| `gcode/original/` | The UltiMaker Cura 5.12.0 G-code files used to print r1–r5 (Creality Ender-3 V3 SE Standard Quality profile, 0.16 mm layers, 10% infill, tree supports). These are the source of the original estimates in `data/cura_estimates_original.csv`. |
| `gcode/controlled_reslice/` | PrusaSlicer 2.7.2 profiles (`ender3v3se_pla.ini`, `nosupport.ini`) and the 20 G-code files of the controlled re-slice: `A_` as printed with supports, `N_` as printed without supports (condition A0), `B_` lip down, `C_` on side. |
| `scripts/` | Python scripts for the mesh analysis (trimesh 5.1.1), overhang areas, opening positions, revision-to-revision comparison, per-feature print-time planner and figures. Run them from the repository root (see below). |
| `data/` | CSV files for every table in the paper, the caliper measurements and the interface acceptance check. |
| `figures/` | Figures 1–5 of the paper (`Fig1_labelled.jpg`, `FigR_revisions_rendered.png`, `FigE2_changes_r4_to_r5.png`, `FigH_time_support_overhang.png`, `FigG_print_time_by_feature.png`) and supplementary Figure S1, `FigS1_changes_r3_to_r4.png` (surface changes from r3 to r4: red = surfaces of r3 removed in r4, blue = surfaces of r4 not present in r3, grey = within 0.05 mm). |

## Reproducing the controlled re-slice

```
prusa-slicer --export-gcode --load gcode/controlled_reslice/ender3v3se_pla.ini --center 110,110 --output A_r1.gcode stl/r1.stl
python3 -I scripts/gcode_planner.py A_r1.gcode
```

Orientation B adds `--rotate-x 180`, orientation C adds `--rotate-x 90`, and condition A0 uses `nosupport.ini`.

## Running the scripts

Install the dependencies with `pip install -r requirements.txt`, then run each script from the repository root:

| Script | Command | Output |
|---|---|---|
| Geometry, volume, area, bounding box, overhang area by orientation | `python3 scripts/stl_analysis.py stl/r1.stl stl/r2.stl stl/r3.stl stl/r4.stl stl/r5.stl` | printed to screen |
| USB-C and button-hole size and position | `python3 scripts/openings.py r1 r3 r4 r5` | `results/openings.json` |
| Overhang area split by feature (lip, wall openings, lugs) | `python3 scripts/overhang_features.py r1 r2 r3 r4 r5` | `results/overhang_features.json` |
| Wall profile and openings around the ring | `python3 scripts/profile.py r5`, `python3 scripts/angular.py r5` | printed to screen |
| Where volume changed between two revisions | `python3 scripts/slicediff.py r4 r5` | printed to screen |
| Per-feature print time from G-code | `python3 scripts/gcode_planner.py --jerk 8 --accel 2500 gcode/controlled_reslice/A_r5.gcode` | JSON printed to screen |
| Figures 2, 3, 4, 5 and S1 | `python3 scripts/fig_revs.py`, `scripts/difffig.py`, `scripts/fig_two.py`, `scripts/fig_feature.py` | `figures/` |

The planner's totals are within 2.2–3.4% of PrusaSlicer's own estimates; in the paper, the per-feature times were scaled so that they add up to the slicer's total (`data/controlled_reslice_feature_times.csv`).

## Measurements

Caliper: MGW Precision DIGE150, 0.01 mm resolution. See `data/caliper_measurements.csv`.
