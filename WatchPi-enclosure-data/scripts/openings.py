import os; os.makedirs('results', exist_ok=True)
import trimesh, numpy as np, sys, json, warnings
from shapely.geometry import LineString
from shapely.ops import unary_union
from shapely import prepared
warnings.filterwarnings("ignore")
def norm(m):
    m=m.copy(); c=(m.bounds[0]+m.bounds[1])/2; m.apply_translation([-c[0],-c[1],-m.bounds[0][2]]); return m
IDr={'r1':18.5,'r2':18.69,'r3':18.68,'r4':18.68,'r5':18.68}
ODr={'r1':20.5,'r2':22.5,'r3':23.0,'r4':23.0,'r5':23.0}
wins={'button_0deg':(-20,20),'button_180deg':(160,200),'usbc_270deg':(225,315)}
res={}
for r in sys.argv[1:]:
    m=norm(trimesh.load(f'stl/{r}.stl'))
    zs=np.arange(0.05,m.bounds[1][2],0.05)
    R0,R1=IDr[r]+0.15,ODr[r]-0.15
    maps={k:[] for k in wins}
    for z in zs:
        s=m.section(plane_origin=[0,0,z],plane_normal=[0,0,1])
        geo=unary_union(list(s.to_planar(to_2D=np.eye(4))[0].polygons_full)); pg=prepared.prep(geo)
        for k,(a0,a1) in wins.items():
            row=[]
            for a in np.radians(np.arange(a0,a1,0.2)):
                seg=LineString([(R0*np.cos(a),R0*np.sin(a)),(R1*np.cos(a),R1*np.sin(a))])
                row.append(0 if pg.intersects(seg) else 1)
            maps[k].append(row)
    out={}
    for k,(a0,a1) in wins.items():
        M=np.array(maps[k]); angs=np.arange(a0,a1,0.2)
        if M.sum()==0: out[k]=None; continue
        zi,ai=np.nonzero(M)
        zlo,zhi=zs[zi.min()],zs[zi.max()]; alo,ahi=angs[ai.min()],angs[ai.max()]
        Rm=(R0+R1)/2
        out[k]={'z_bottom':round(float(zlo),2),'z_top':round(float(zhi),2),'height_mm':round(float(zhi-zlo+0.05),2),
                'centre_z':round(float((zlo+zhi)/2),2),'angle_deg':[round(float(alo),1),round(float(ahi),1)],
                'width_mm_at_mid_wall':round(float(np.radians(ahi-alo+0.2)*Rm),2),'centre_angle':round(float((alo+ahi)/2),1),
                'open_area_mm2_unwrapped':round(float(M.sum()*0.05*np.radians(0.2)*Rm),2)}
        np.save(f'results/open_{r}_{k}.npy',M)
    res[r]=out; print(r,json.dumps(out))
json.dump(res,open('results/openings.json','w'),indent=1)
