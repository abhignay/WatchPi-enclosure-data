import os; os.makedirs('results', exist_ok=True)
import trimesh, numpy as np, sys, json
def norm(m):
    m=m.copy(); c=(m.bounds[0]+m.bounds[1])/2; m.apply_translation([-c[0],-c[1],-m.bounds[0][2]]); return m
IDr={'r1':18.5,'r2':18.69,'r3':18.68,'r4':18.68,'r5':18.68}
ODr={'r1':20.5,'r2':22.5,'r3':23.0,'r4':23.0,'r5':23.0}
res={}
for r in sys.argv[1:]:
    m=norm(trimesh.load(f'stl/{r}.stl'))
    n=m.face_normals; A=m.area_faces; c=m.triangles_center
    rad=np.hypot(c[:,0],c[:,1]); ang=np.degrees(np.arctan2(c[:,1],c[:,0]))%360; z=c[:,2]
    oh=(n[:,2]< -np.cos(np.radians(50)))&(z>0.05)
    cls=np.full(len(A),'other',dtype=object)
    cls[(rad<IDr[r]-0.05)]='inner lip / ledge (inside ID)'
    cls[(rad>=IDr[r]-0.05)&(rad<=ODr[r]+0.1)]='wall openings / pockets'
    cls[(rad>ODr[r]+0.1)]='lugs / outer features'
    out={}
    for k in ['inner lip / ledge (inside ID)','wall openings / pockets','lugs / outer features']:
        s=oh&(cls==k)
        out[k]={'area':round(float(A[s].sum()),1),'area_x_height':round(float((A[s]*z[s]).sum()),0),
                'z_range':[round(float(z[s].min()),2),round(float(z[s].max()),2)] if s.any() else None}
    out['TOTAL']={'area':round(float(A[oh].sum()),1),'area_x_height':round(float((A[oh]*z[oh]).sum()),0)}
    res[r]=out
    print(r,json.dumps(out))
json.dump(res,open('results/overhang_features.json','w'),indent=1)
sup=np.array([0.769,0.130,0.751,0.894,0.873])
tot=np.array([res[k]['TOTAL']['area'] for k in res]); vol=np.array([res[k]['TOTAL']['area_x_height'] for k in res])
print('r(support, overhang area)=%.2f  r(support, area*height)=%.2f'%(np.corrcoef(sup,tot)[0,1],np.corrcoef(sup,vol)[0,1]))
