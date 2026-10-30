import json, numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
plt.rcParams['font.family']='Times New Roman'
d=json.load(open('wb_g.json'))[1]
g={int(r['date']):round(r['value'],1) for r in d if 2000<=int(r['date'])<=2025}
yrs=list(range(2000,2026)); v=[g[y] for y in yrs]
# (inicio, fin, tipo)
periods=[(2000,2001,'rec'),(2002,2008,'exp'),(2009,2009,'des'),(2010,2014,'exp'),(2015,2015,'des'),(2016,2016,'rcs'),
         (2017,2017,'rec'),(2018,2019,'des'),(2020,2020,'rcs'),(2021,2022,'rec'),(2023,2023,'des'),(2024,2024,'rcs'),(2025,2025,'rec')]
col={'exp':'#2E7D32','des':'#F9A825','rcs':'#C62828','rec':'#1565C0'}
lab={'exp':'Expansión','des':'Desaceleración','rcs':'Recesión','rec':'Recuperación'}
fig,ax=plt.subplots(figsize=(10,5.4),dpi=300)
for a,b,t in periods: ax.axvspan(a-0.5,b+0.5,color=col[t],alpha=0.16,lw=0)
ax.axhline(0,color='#444',ls='--',lw=0.9)
ax.plot(yrs,v,color='#003366',lw=2,marker='o',ms=5,zorder=3,label='Variación anual del PIB real')
m,b0=np.polyfit(yrs,v,1)
ax.plot(yrs,[m*y+b0 for y in yrs],color='#555',lw=1.2,ls=':',label='Tendencia lineal')
ax.axhline(np.mean(v),color='#8E24AA',lw=1,ls='-.',label=f'Promedio 2000–2025 ({np.mean(v):.1f} %)'.replace('.',',')+'')
off={2021:(0,8),2011:(0,8),2013:(0,8),2004:(0,8),2020:(0,-14),2024:(0,-14),2016:(0,-14),2025:(8,8)}
for y in yrs:
    dx,dy=off.get(y,(0,8)) if y in off or True else (0,8)
    if y in (2002,2003,2005,2006,2007,2008,2009,2010,2012,2014,2015,2017,2018,2019,2022,2023,2000,2001): 
        dy=8 if v[y-2000]>=0 else -14
        if y in (2007,2009,2015,2019,2018,2023): dy=-14 if v[y-2000]<3 else 8
    ax.annotate(f'{g[y]:.1f}'.replace('.',','),(y,g[y]),textcoords='offset points',xytext=(dx,dy),ha='center',fontsize=7.5,color='#111')
ax.set_xticks(yrs); ax.set_xticklabels(yrs,rotation=60,fontsize=8)
ax.set_xlim(1999.5,2025.5); ax.set_ylim(-11.5,11.5)
ax.set_ylabel('Variación porcentual anual (%)',fontsize=10); ax.set_xlabel('Año',fontsize=10)
ax.grid(axis='y',alpha=0.3)
for s in ('top','right'): ax.spines[s].set_visible(False)
h=[Patch(color=col[k],alpha=0.4,label=lab[k]) for k in ('exp','des','rcs','rec')]
h1,l1=ax.get_legend_handles_labels()
ax.legend(handles=h1+h,loc='lower left',fontsize=8,ncol=2,frameon=True,framealpha=0.95)
plt.tight_layout(); plt.savefig('fig_pib.png',dpi=300)
print('trend slope',m)
