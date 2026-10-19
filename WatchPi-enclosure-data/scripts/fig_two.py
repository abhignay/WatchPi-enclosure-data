import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.family":"serif","font.serif":["Liberation Serif","DejaVu Serif"],"font.size":11,
 "axes.spines.top":False,"axes.spines.right":False,"axes.edgecolor":"#52514e","xtick.color":"#52514e","ytick.color":"#52514e","savefig.dpi":300})
rev=["r1","r2","r3","r4","r5"]; t=np.array([53.27,44.90,66.17,80.62,80.22]); S=np.array([0.769,0.130,0.751,0.894,0.873]); oh=np.array([285.6,146.0,275.9,313.0,320.8])
B="#2a78d6"
fig,(a1,a2)=plt.subplots(1,2,figsize=(10,3.9))
for ax in (a1,a2): ax.grid(True,color="#e4e3df",lw=0.8); ax.set_axisbelow(True)
a1.scatter(S,t,s=60,color=B,edgecolor="white",linewidth=1.5,zorder=3)
for r,x,y,o in zip(rev,S,t,[(6,-4),(6,-4),(6,-4),(6,4),(-18,-12)]): a1.annotate(r,(x,y),textcoords="offset points",xytext=o)
a1.set_xlabel("Support filament (m)"); a1.set_ylabel("Estimated print time (min)"); a1.set_xlim(0,1.0); a1.set_ylim(35,90)
a1.set_title("(a)",loc="left",fontweight="bold")
a2.scatter(oh,S,s=60,color=B,edgecolor="white",linewidth=1.5,zorder=3)
for r,x,y,o in zip(rev,oh,S,[(7,3),(6,-4),(-18,-13),(-18,4),(6,-4)]): a2.annotate(r,(x,y),textcoords="offset points",xytext=o)
a2.set_xlabel("STL overhang area, >50° from vertical (mm²)"); a2.set_ylabel("Support filament (m)"); a2.set_xlim(100,350); a2.set_ylim(0,1.0)
a2.set_title("(b)",loc="left",fontweight="bold")
fig.tight_layout(); fig.savefig("figures/FigH_time_support_overhang.png")
