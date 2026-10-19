import trimesh, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.patches import Patch
plt.rcParams.update({"font.family":"serif","font.serif":["Liberation Serif","DejaVu Serif"],"font.size":10})
def norm(m):
    m=m.copy(); c=(m.bounds[0]+m.bounds[1])/2; m.apply_translation([-c[0],-c[1],-m.bounds[0][2]]); return m
L=np.array([0.3,-0.6,0.75]); L/=np.linalg.norm(L)
GREY=np.array([0.80,0.80,0.82]); BLUE=np.array([0.16,0.47,0.84]); RED=np.array([0.89,0.29,0.28])
def changed(m,other,tol=0.05):
    pts=m.triangles_center
    _,d,_=trimesh.proximity.closest_point(other,pts)
    return d>tol
def draw(ax,m,mask,hl,el,az,title):
    sh=np.clip(m.face_normals@L,0,1)*0.6+0.4
    col=np.where(mask[:,None],hl[None,:],GREY[None,:])*sh[:,None]
    ax.add_collection3d(Poly3DCollection(m.triangles,facecolors=np.c_[col,np.ones(len(col))],edgecolor='none'))
    ax.set_xlim(-25,25); ax.set_ylim(-25,25); ax.set_zlim(-18,32); ax.view_init(el,az); ax.set_axis_off(); ax.set_box_aspect((1,1,1)); ax.set_title(title,fontsize=10)
views=[(30,-20,'+X side'),(30,160,'−X side'),(30,-90,'USB-C side')]
for A,B,fn in [('r3','r4','FigS1_changes_r3_to_r4.png'),('r4','r5','FigE2_changes_r4_to_r5.png')]:
    a=norm(trimesh.load(f'stl/{A}.stl')); b=norm(trimesh.load(f'stl/{B}.stl'))
    ma=changed(a,b); mb=changed(b,a)
    fig=plt.figure(figsize=(12,7.4))
    for i,(el,az,lab) in enumerate(views):
        draw(fig.add_subplot(2,3,i+1,projection='3d'),a,ma,RED,el,az,f'{A} ({lab}) – surfaces removed in {B}')
        draw(fig.add_subplot(2,3,i+4,projection='3d'),b,mb,BLUE,el,az,f'{B} ({lab}) – surfaces new in {B}')
    fig.legend(handles=[Patch(color=RED,label=f'Surface of {A} that no longer exists in {B}'),Patch(color=BLUE,label=f'Surface of {B} not present in {A}'),Patch(color=GREY,label='Unchanged (within 0.05 mm)')],loc='lower center',ncol=3,frameon=False)
    plt.tight_layout(rect=(0,0.05,1,1)); plt.savefig('figures/'+fn,dpi=200); plt.close()
    print(fn, 'changed faces', ma.sum(), mb.sum())
