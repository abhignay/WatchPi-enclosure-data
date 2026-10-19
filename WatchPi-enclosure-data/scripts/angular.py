import trimesh, numpy as np, sys, warnings
from shapely.geometry import LineString
from shapely.ops import unary_union
warnings.filterwarnings("ignore")
def norm(m):
    m=m.copy(); c=(m.bounds[0]+m.bounds[1])/2; m.apply_translation([-c[0],-c[1],-m.bounds[0][2]]); return m
def runs(mask, ang):
    out=[]; i=0; n=len(mask)
    while i<n:
        if mask[i]:
            j=i
            while j+1<n and mask[j+1]: j+=1
            out.append((ang[i],ang[j])); i=j+1
        else: i+=1
    return out
for r in sys.argv[1:]:
    m=norm(trimesh.load(f'stl/{r}.stl'))
    ang=np.arange(0,360,0.5)
    print('==',r)
    for z in [1.0,3.0,5.0,7.0,9.0,11.0,12.5]:
        if z>m.bounds[1][2]: continue
        s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
        geo=unary_union(list(s.to_planar(to_2D=np.eye(4))[0].polygons_full))
        rin=np.full(len(ang),np.nan); rout=np.full(len(ang),np.nan)
        for k,a in enumerate(np.radians(ang)):
            it=LineString([(5*np.cos(a),5*np.sin(a)),(24.5*np.cos(a),24.5*np.sin(a))]).intersection(geo)
            if it.is_empty: continue
            gs=[it] if it.geom_type=='LineString' else list(it.geoms)
            d=[np.linalg.norm(c) for g in gs for c in g.coords]; rin[k]=min(d); rout[k]=max(d)
        base=np.nanmedian(rin)
        gaps=runs(np.isnan(rin),ang)
        groove=runs((rin>base+0.3)&~np.isnan(rin),ang)
        print(f' z={z:4.1f} ID={2*base:.2f} OD~{2*np.nanmedian(rout):.2f} through-openings(deg)={gaps} inner-recess(deg)={[(a,b,round(np.nanmax(rin[(ang>=a)&(ang<=b)]),2)) for a,b in groove]}')
