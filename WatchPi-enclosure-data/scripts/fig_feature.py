import csv, os, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
plt.rcParams.update({"font.family":"serif","font.serif":["Liberation Serif","DejaVu Serif"],"font.size":11,
 "axes.spines.top":False,"axes.spines.right":False,"axes.edgecolor":"#52514e","xtick.color":"#52514e","ytick.color":"#52514e","savefig.dpi":300})
rev=['r1','r2','r3','r4','r5']
D={}
for row in csv.DictReader(open('data/controlled_reslice_feature_times.csv')):
    tag={'A_as_printed':'A_','A0_supports_off':'N_'}.get(row['condition'])
    if tag: D[tag+row['revision']]={'Walls_min':float(row['walls_min']),'Infill_min':float(row['infill_skin_min']),'Travel_min':float(row['travel_min']),
        'Other_min':float(row['other_min']),'Support_min':float(row['support_min']),'slicer_min':float(row['total_min'])}
cats=[('Walls_min','Walls (perimeters)','#2a78d6',None),('Infill_min','Infill and skin','#1baf7a',None),
      ('Travel_min','Travel','#eda100',None),('Other_min','Other (retracts, skirt)','#6250d6',None),('Support_min','Support','#eb6834','///')]
fig,ax=plt.subplots(figsize=(6.2,4.0)); ax.yaxis.grid(True,color="#e4e3df",lw=0.8); ax.set_axisbelow(True)
bottom=np.zeros(5)
for key,lab,col,h in cats:
    v=np.array([D['A_'+r][key] for r in rev])
    ax.bar(rev,v,bottom=bottom,width=0.58,color=col,hatch=h,edgecolor='white',linewidth=1.2,label=lab)
    if key=='Support_min':
        for i,(b,x) in enumerate(zip(bottom,v)):
            ax.text(i,b+x+0.6,f"{x:.1f} min\n({100*x/(b+x):.0f}%)",ha='center',va='bottom',fontsize=8.5,color='#0b0b0b')
    bottom+=v
N=np.array([D['N_'+r]['slicer_min'] for r in rev])
ax.scatter(range(5),N,marker='_',s=500,color='#0b0b0b',zorder=4,linewidths=2,label='Same part sliced without supports')
ax.set_ylabel('Estimated print time (min)'); ax.set_xlabel('Enclosure revision'); ax.set_ylim(0,60)
ax.legend(frameon=False,fontsize=8.5,loc='upper left',ncol=2)
fig.tight_layout(); fig.savefig('figures/FigG_print_time_by_feature.png'); plt.close()
