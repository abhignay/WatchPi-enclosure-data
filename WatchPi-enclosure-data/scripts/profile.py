import trimesh, numpy as np, sys
from shapely.geometry import LineString
from shapely.ops import unary_union
import warnings; warnings.filterwarnings("ignore")
def norm(m):
    m=m.copy(); c=(m.bounds[0]+m.bounds[1])/2; m.apply_translation([-c[0],-c[1],-m.bounds[0][2]]); return m
for r in sys.argv[1:]:
    m=norm(trimesh.load(f'stl/{r}.stl'))
    print('==',r,'height',round(m.bounds[1][2],2))
    for ang in [45,135,225,315]:
        a=np.radians(ang); rows=[]
        for z in np.arange(0.1,m.bounds[1][2],0.5):
            s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
            if s is None: rows.append((z,None)); continue
            geo=unary_union(list(s.to_planar(to_2D=np.eye(4))[0].polygons_full))
            seg=LineString([(5*np.cos(a),5*np.sin(a)),(35*np.cos(a),35*np.sin(a))])
            it=seg.intersection(geo)
            if it.is_empty: rows.append((z,None)); continue
            gs=[it] if it.geom_type=='LineString' else list(it.geoms)
            rows.append((z,[(round(np.linalg.norm(g.coords[0]),2),round(np.linalg.norm(g.coords[-1]),2)) for g in gs]))
        print(' ang',ang, ' '.join(f"z{z:.1f}:{v}" for z,v in rows[::2]))
