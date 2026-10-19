import trimesh, numpy as np, sys, warnings
from shapely.ops import unary_union
warnings.filterwarnings("ignore")
def norm(m):
    m=m.copy(); c=(m.bounds[0]+m.bounds[1])/2; m.apply_translation([-c[0],-c[1],-m.bounds[0][2]]); return m
A,B=sys.argv[1],sys.argv[2]
a=norm(trimesh.load(f'stl/{A}.stl')); b=norm(trimesh.load(f'stl/{B}.stl'))
dz=0.05; zs=np.arange(dz/2,min(a.bounds[1][2],b.bounds[1][2]),dz)
from collections import defaultdict
acc=defaultdict(float)
def sec(m,z):
    s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
    return unary_union(list(s.to_planar(to_2D=np.eye(4))[0].polygons_full)) if s is not None else None
tot_add=tot_rem=0
for z in zs:
    ga,gb=sec(a,z),sec(b,z)
    add=gb.difference(ga); rem=ga.difference(gb)
    for lab,g,sgn in (('added',add,1),('removed',rem,-1)):
        geoms=[g] if g.geom_type=='Polygon' else list(getattr(g,'geoms',[]))
        for p in geoms:
            if p.area<1e-4: continue
            c=p.centroid; ang=np.degrees(np.arctan2(c.y,c.x))%360; rad=np.hypot(c.x,c.y)
            key=(lab, int(((ang+7.5)%360)//15*15), 'inside ID' if rad<18.6 else ('wall' if rad<23.1 else 'outside'), int(z//2*2))
            acc[key]+=p.area*dz
            if sgn>0: tot_add+=p.area*dz
            else: tot_rem+=p.area*dz
print(f'{B} vs {A}: added {tot_add:.1f} mm3, removed {tot_rem:.1f} mm3, net {tot_add-tot_rem:+.1f}')
agg=defaultdict(float)
for (lab,ang,reg,zb),v in acc.items(): agg[(lab,ang,reg)]+=v
for k,v in sorted(agg.items(),key=lambda kv:-kv[1])[:14]:
    zsplit={zb:round(vv,1) for (l,an,rg,zb),vv in acc.items() if (l,an,rg)==k and vv>0.5}
    print(f'  {k[0]:8s} angle~{k[1]:3d}deg {k[2]:10s} {v:7.1f} mm3   by z-band {zsplit}')
