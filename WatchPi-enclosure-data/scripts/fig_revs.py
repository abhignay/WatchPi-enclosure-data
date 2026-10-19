import trimesh, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
plt.rcParams.update({"font.family":"serif","font.serif":["Liberation Serif","DejaVu Serif"],"font.size":11})
def norm(m):
    m=m.copy(); c=(m.bounds[0]+m.bounds[1])/2; m.apply_translation([-c[0],-c[1],-m.bounds[0][2]]); return m
L=np.array([0.35,-0.55,0.76]); L/=np.linalg.norm(L)
fig=plt.figure(figsize=(14,4.6))
views=[(22,-90,'USB-C side'),(22,0,'button side')]
for j,(el,az,lab) in enumerate(views):
    for i,r in enumerate(['r1','r2','r3','r4','r5']):
        m=norm(trimesh.load(f'stl/{r}.stl'))
        ax=fig.add_subplot(2,5,j*5+i+1,projection='3d')
        Lr=L.copy()
        R=trimesh.transformations.rotation_matrix(np.radians(az+90),[0,0,1])[:3,:3]; Lr=R@L
        sh=np.clip(m.face_normals@Lr,0,1)*0.65+0.3
        col=np.outer(sh,[0.45,0.5,0.6])
        ax.add_collection3d(Poly3DCollection(m.triangles,facecolors=np.c_[col,np.ones(len(col))],edgecolor='none'))
        ax.set_xlim(-25,25); ax.set_ylim(-25,25); ax.set_zlim(-3,18); ax.view_init(el,az); ax.set_axis_off(); ax.set_box_aspect((1,1,0.42),zoom=1.35)
        if j==0: ax.set_title(r,fontsize=14,fontweight='bold')
    fig.text(0.005,0.70 if j==0 else 0.25,f'View from {lab}',rotation=90,va='center',fontsize=11)
plt.subplots_adjust(left=0.03,right=0.995,top=0.93,bottom=0.01,wspace=0.0,hspace=0.0)
plt.savefig('figures/FigR_revisions_rendered.png',dpi=200)
