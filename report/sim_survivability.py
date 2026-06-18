"""
SPACE-BASED AI DATA CENTERS, PART II  --  Survivability, Reliability & Launch Architecture
==========================================================================================
Verified-data edition (June 2026). Every figure carries a DATA SOURCE credit line.
All inputs are traceable to primary sources (NASA, ESA, FCC, NRLMSIS, vendor datasheets,
and Google's Project Suncatcher paper arXiv:2511.19468). First-order models, honest
uncertainty bands. Reproduce with: python sim_survivability.py

Key verified inputs and their sources are listed in SOURCES{} at the bottom.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from matplotlib.patches import Rectangle, FancyBboxPatch
import matplotlib as mpl

# ---------------------------------------------------------------- house style (agency-grade)
mpl.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9.5,
    "axes.titlesize": 11.5, "axes.titleweight": "bold",
    "axes.labelsize": 10, "axes.edgecolor": "#33414f", "axes.linewidth": 1.0,
    "axes.grid": True, "grid.color": "#e6e9ec", "grid.linewidth": 0.8,
    "xtick.color": "#33414f", "ytick.color": "#33414f",
    "figure.dpi": 135, "savefig.dpi": 175, "savefig.bbox": "tight",
    "legend.frameon": False,
})
NAVY="#16243a"; ACCENT="#c75c2e"; COOL="#2f6f8f"; GOOD="#2e7d4f"; WARN="#caa12a"; BAD="#a3303a"
OUT="C:/Users/samar/Downloads/Space_DataCenter_ReportII/figures/"

def credit(fig, text):
    fig.text(0.005, -0.02, "DATA SOURCE  "+text, ha="left", va="top",
             fontsize=6.7, color="#7a8590", style="italic")
def figtab(fig, label):
    fig.text(0.005, 1.005, label, ha="left", va="bottom", fontsize=10.5,
             fontweight="bold", color="white",
             bbox=dict(boxstyle="round,pad=0.32", fc=NAVY, ec="none"))

# physical constants
MU=3.986004418e14; RE=6371e3; SIG=5.670374419e-8; G0=9.80665; S0=1361.0
D={}   # digest of computed headline numbers

# ==========================================================================================
# DENSITY MODEL  -- NRLMSIS 2.1 anchors (verified), three solar-activity scenarios
# kg/m^3.  Anchors at 600/650/700/800 km are computed NRLMSIS values; lower-alt entries
# extend the profile with realistic scale heights for plotting only.
# ==========================================================================================
alt_a = np.array([450,500,550,600,650,700,800])*1e3
rho_min  = np.array([1.3e-13,6.0e-14,3.5e-14,2.0e-14,1.1e-14,6.8e-15,3.5e-15])  # F10.7~65
rho_mod  = np.array([1.8e-12,9.0e-13,4.8e-13,3.0e-13,1.6e-13,8.3e-14,2.7e-14])  # F10.7~140
rho_max  = np.array([6.0e-12,4.0e-12,2.9e-12,2.1e-12,1.2e-12,7.1e-13,2.6e-13])  # F10.7~250
def rho(h, tab):
    h=np.clip(h, alt_a[0], alt_a[-1]); return np.exp(np.interp(h, alt_a, np.log(tab)))

def decay_years(h0_km, BCinv, tab, cd=2.2):
    a=RE+h0_km*1e3; t=0.0; yr=3.15576e7; dt=3600*6
    while a>RE+120e3 and t<2000*yr:
        h=a-RE
        a+=-cd*BCinv*rho(h,tab)*np.sqrt(MU*a)*dt; t+=dt
        dt = 3600*48 if (a-RE)>500e3 else (3600*12 if (a-RE)>300e3 else 3600*2)
    return t/yr

# Reference data-center bus (Report I mass budget m=415 kg).
m_sat=415.0
Am_compact=3.5/m_sat        # arrays feathered (realistic operating attitude)
Am_dense  =1.5/m_sat
for sc,tab in [("min",rho_min),("mod",rho_mod),("max",rho_max)]:
    D[f"decay650_{sc}"]=decay_years(650,Am_compact,tab)
RULE_FCC=5; RULE_INTL=25

# ---- Fig 1 : orbital decay with solar-cycle band + FCC 5-yr rule
alts=np.linspace(450,800,24)
fig=plt.figure(figsize=(8.6,5.3)); ax=fig.add_subplot(111)
dy_min=[decay_years(h,Am_compact,rho_min) for h in alts]
dy_mod=[decay_years(h,Am_compact,rho_mod) for h in alts]
dy_max=[decay_years(h,Am_compact,rho_max) for h in alts]
ax.fill_between(alts,dy_max,dy_min,color=COOL,alpha=0.16,label="solar-cycle range (min↔max)")
ax.semilogy(alts,dy_mod,color=COOL,lw=2.6,label="moderate solar activity (F10.7≈140)")
ax.axhline(RULE_FCC,color=BAD,ls="--",lw=1.5); ax.text(452,RULE_FCC*1.1,"FCC 5-yr rule (since 2022, effective 2024)",color=BAD,fontsize=8.3)
ax.axhline(RULE_INTL,color="#555",ls=":",lw=1.2); ax.text(452,RULE_INTL*1.1,"25-yr international baseline",color="#555",fontsize=8.3)
ax.axvline(650,color="#999",ls=":",lw=1.1); ax.text(655,2.2e3,"Suncatcher\n650 km",fontsize=8.5,color="#555")
ax.set_xlabel("Initial circular altitude (km)"); ax.set_ylabel("Natural orbital lifetime (years, log)")
ax.set_title("Natural decay fails the 5-year disposal rule at 650 km  →  active de-orbit is mandatory")
ax.set_ylim(0.7,5e3); ax.legend(loc="upper left",fontsize=8.5)
ax.text(0.99,0.03,f"650 km, realistic bus (A/m=0.008):\nsolar-max {D['decay650_max']:.0f} yr · moderate {D['decay650_mod']:.0f} yr · solar-min {D['decay650_min']:.0f} yr\n"
        "Only a solar-max launch comes close to 5 yr. Propulsion required.",
        transform=ax.transAxes,ha="right",va="bottom",fontsize=8,
        bbox=dict(boxstyle="round,pad=0.4",fc="#fdf3ec",ec=ACCENT))
figtab(fig,"FIG. 1"); credit(fig,"Atmospheric density: NRLMSIS 2.1 (Picone et al. 2002). Disposal rule: FCC 22-74 (2022). Drag: circular-orbit model, C_D=2.2.")
fig.savefig(OUT+"fig1_orbital_decay.png"); plt.close(fig)

# ==========================================================================================
# Fig 2 : THE THERMAL WALL  (a) radiator area scaling  (b) chip-interface saturation
# ==========================================================================================
def rad_area(Q,T_C,eps=0.90,sided=2,paras=0.12):
    T=T_C+273.15; return Q/(eps*SIG*T**4*sided*(1-paras))
Q=np.logspace(np.log10(300),np.log10(2e6),250)
fig=plt.figure(figsize=(10.0,5.2)); gs=gridspec.GridSpec(1,2,width_ratios=[1.18,1],wspace=0.36)
axA=fig.add_subplot(gs[0])
for T_C,c in [(20,COOL),(40,WARN),(60,ACCENT)]:
    axA.loglog(Q/1e3,rad_area(Q,T_C),lw=2.5,color=c,label=f"radiator @ {T_C} °C")
def mark(qkW,T,name,dx,dy,c):
    A=rad_area(qkW*1e3,T); axA.scatter([qkW],[A],s=52,color=c,ec="white",lw=1.1,zorder=5)
    axA.annotate(f"{name}\n{A:,.0f} m²",(qkW,A),xytext=(qkW*dx,A*dy),fontsize=7.8,color=c)
mark(0.85,20,"Starcloud-1\n1× H100, 0.85 kW",1.25,0.30,COOL)
mark(1.45,20,"Report I\n4 TPU, 1.45 kW",0.22,1.7,GOOD)
mark(120,40,"GB200 NVL72\nrack, 120 kW",0.16,0.40,ACCENT)
mark(1000,40,"1 MW node",0.18,0.40,BAD)
axA.scatter([1000],[1200],marker="*",s=170,color="k",zorder=6)
axA.annotate("Industry rule\n~1,200 m²/MW",(1000,1200),xytext=(150,2100),fontsize=7.8,color="k")
axA.set_xlabel("Compute heat load (kW, log)"); axA.set_ylabel("Required radiator area (m², log)")
axA.set_title("(a) Cooling scales linearly with power")
axA.legend(loc="upper left",fontsize=8)
D["area_1MW_20"]=rad_area(1e6,20); D["area_1MW_60"]=rad_area(1e6,60)

# (b) chip-to-radiator interface temperature rise = P * R_th ; passive chains saturate
axB=fig.add_subplot(gs[1])
chips=[("TPU v6e\n~200 W*",200,COOL),("TPU\n300 W",300,"#7fa8bd"),
       ("H100\n700 W",700,WARN),("B200\n1000 W",1000,ACCENT),("GB200\n1200 W",1200,BAD)]
Rth=0.30   # Report I passive chain (K/W)
xs=np.arange(len(chips))
dT=[p*Rth for _,p,_ in chips]
bars=axB.bar(xs,dT,color=[c for *_,c in chips],width=0.66)
axB.axhline(125,color=BAD,ls="--",lw=1.4); axB.text(0.1,128,"125 °C junction limit (entire budget)",color=BAD,fontsize=7.8)
for b,v in zip(bars,dT): axB.text(b.get_x()+b.get_width()/2,v+4,f"{v:.0f}",ha="center",fontsize=8)
axB.set_xticks(xs); axB.set_xticklabels([c[0] for c in chips],fontsize=7.6)
axB.set_ylabel("Junction→radiator ΔT at R_th=0.30 K/W (°C)")
axB.set_title("(b) Passive chain saturates >400 W")
axB.set_ylim(0,400)
axB.text(0.5,-0.30,"Above the H100, P·R_th alone exceeds the whole 125 °C budget →\nchip-level liquid/loop-heat-pipe cooling becomes mandatory, not optional.",
         transform=axB.transAxes,ha="center",fontsize=7.6,color="#444")
figtab(fig,"FIG. 2"); credit(fig,"Stefan-Boltzmann (ε=0.90, double-sided, 12% parasitic). TDPs: NVIDIA datasheets (H100 700W, B200 1000W, GB200 1200W); *TPU v6e undisclosed, ~200W est. (The Next Platform).")
fig.savefig(OUT+"fig2_thermal_wall.png"); plt.close(fig)

# ==========================================================================================
# Fig 3 : DEBRIS  (a) catastrophic collision probability  (b) cascade coupling
# Flux >1cm at SSO 650-800 km: 1e-5 .. 1e-4 /m^2/yr (ORDEM 3.1 / MASTER-8). central 3e-5.
# ==========================================================================================
flo,fmid,fhi=1e-5,3e-5,1e-4
A_sil=15.0; N=81; yrs=np.linspace(0,10,200)
Pany=lambda f,t: (1-np.exp(-f*A_sil*N*t))*100
fig=plt.figure(figsize=(9.0,5.0)); gs=gridspec.GridSpec(1,2,width_ratios=[1.4,1],wspace=0.30)
axA=fig.add_subplot(gs[0])
axA.fill_between(yrs,Pany(flo,yrs),Pany(fhi,yrs),color=ACCENT,alpha=0.16,label="ORDEM/MASTER range (1e-5–1e-4)")
axA.plot(yrs,Pany(fmid,yrs),color=ACCENT,lw=2.6,label="central (3e-5 /m²/yr)")
axA.axvline(5,color="#999",ls=":",lw=1.1); axA.text(5.07,3,"5-yr design life",fontsize=8.3,color="#555")
axA.set_xlabel("Mission elapsed time (years)"); axA.set_ylabel("P(≥1 catastrophic >1 cm hit in 81-sat cluster) [%]")
axA.set_title("(a) Catastrophic debris risk, full cluster"); axA.legend(loc="upper left",fontsize=8)
D["Pcat5_mid"]=Pany(fmid,5); D["Pcat5_lo"]=Pany(flo,5); D["Pcat5_hi"]=Pany(fhi,5); D["Pcat10_mid"]=Pany(fmid,10)
axA.text(0.99,0.03,f"5-yr: {D['Pcat5_lo']:.0f}–{D['Pcat5_hi']:.0f}% (central {D['Pcat5_mid']:.0f}%)\nper cluster, single generation",
         transform=axA.transAxes,ha="right",va="bottom",fontsize=8,bbox=dict(boxstyle="round,pad=0.35",fc="#fdf3ec",ec=ACCENT))
axB=fig.add_subplot(gs[1])
spacing=np.array([100,150,200,300,500,1000]); nfrag=2000
nhit=lambda d,r=2.0:(1-np.exp(-nfrag*(np.pi*r**2)/(4*np.pi*d**2)))*100
axB.plot(spacing,[nhit(d) for d in spacing],"o-",color=BAD,lw=2.2)
axB.axvspan(100,200,color=BAD,alpha=0.09); axB.text(150,nhit(150)+1.4,"Suncatcher\n100–200 m",ha="center",fontsize=7.8,color=BAD)
axB.set_xlabel("Formation spacing (m)"); axB.set_ylabel("P(a given neighbor struck by a fragment) [%]")
axB.set_title("(b) In-cluster cascade coupling")
D["nhit150"]=nhit(150)
figtab(fig,"FIG. 3"); credit(fig,"Debris flux: NASA ORDEM 3.1 / ESA MASTER-8 (Horstmann et al., NTRS 20210011563), 800 km SSO. Population: ESA Space Environment Report 2025. Poisson impact model.")
fig.savefig(OUT+"fig3_debris_risk.png"); plt.close(fig)

# ==========================================================================================
# Fig 4 : RADIATION  (a) dose-depth (recalibrated)  (b) reliability/throughput trade
# Calibrated to: ~20-40 krad/yr at 1mm (electron-dominated), proton floor ~100-150 rad/yr
# deep, matching SIRI-1 600km SSO and Google v6e (~150 rad/yr expected, 750 rad/5yr req).
# ==========================================================================================
al=np.linspace(1,20,90)
dose_lo=2.0e4*np.exp(-al/1.7)+100      # rad(Si)/yr  thinner-shield electron-dominated upper
dose_hi=3.8e4*np.exp(-al/1.7)+160
HBM=2000.0; GOOG_YR=150.0
fig=plt.figure(figsize=(9.2,5.0)); gs=gridspec.GridSpec(1,2,width_ratios=[1,1],wspace=0.30)
ax1=fig.add_subplot(gs[0])
ax1.fill_between(al,dose_lo*5,dose_hi*5,color=COOL,alpha=0.16,label="5-yr cumulative (model band)")
ax1.semilogy(al,(dose_lo+dose_hi)/2*5,color=COOL,lw=2.4)
ax1.axhline(HBM,color=BAD,ls="--",lw=1.4); ax1.text(8.5,HBM*1.12,"HBM tolerance ~2 krad(Si)",color=BAD,fontsize=8)
ax1.axhline(750,color=GOOD,ls=":",lw=1.3); ax1.text(8.5,790,"Google 5-yr requirement 750 rad(Si)",color=GOOD,fontsize=7.8)
ax1.axvline(10,color="#999",ls=":",lw=1)
ax1.set_xlabel("Aluminium shielding thickness (mm)"); ax1.set_ylabel("Cumulative 5-yr TID [rad(Si), log]")
ax1.set_title("(a) Dose vs shielding — 10 mm Al closes it"); ax1.legend(loc="upper right",fontsize=8)
D["TID10_5yr"]=(dose_lo[np.argmin(abs(al-10))]+dose_hi[np.argmin(abs(al-10))])/2*5
ax2=fig.add_subplot(gs[1])
prot=["None\n(COTS)","ECC +\ncheckpoint","ECC + sel.\nTMR","Full TMR /\nrad-hard"]
eff=np.array([0.55,0.86,0.78,0.50]); risk=np.array([0.40,0.06,0.02,0.005])
x=np.arange(len(prot))
ax2.bar(x-0.19,eff*100,0.38,color=COOL,label="usable compute %")
ax2.bar(x+0.19,risk*100,0.38,color=BAD,label="uncorrected-error risk %")
ax2.set_xticks(x); ax2.set_xticklabels(prot,fontsize=7.8); ax2.set_ylabel("Percent")
ax2.set_title("(b) Reliability/throughput trade"); ax2.legend(fontsize=7.8,loc="upper right")
ax2.text(0.5,-0.32,"AI inference tolerates bit-flips better than HPC; ECC+checkpoint is the sweet spot.",
         transform=ax2.transAxes,ha="center",fontsize=7.6,color="#444")
figtab(fig,"FIG. 4"); credit(fig,"TID: SHIELDOSE-2 / AE8-AP8 class, calibrated to SIRI-1 (600 km SSO) & Google Suncatcher (arXiv:2511.19468: ~150 rad/yr, 750 rad/5yr, HBM 2 krad). (b) engineering estimate.")
fig.savefig(OUT+"fig4_radiation.png"); plt.close(fig)

# ==========================================================================================
# Fig 5 : DELTA-V & PROPELLANT (corrected density)
# ==========================================================================================
def dv_drag(h,Am,cd=2.2,yr=5,tab=rho_mod):
    a=RE+h*1e3; v=np.sqrt(MU/a); return 0.5*rho(h*1e3,tab)*v**2*cd*Am*3.15576e7*yr
def dv_deorbit(h,hp=180):
    r1=RE+h*1e3; r2=RE+hp*1e3; v1=np.sqrt(MU/r1); return v1*(1-np.sqrt(2*r2/(r1+r2)))
dv_d=dv_drag(650,Am_compact); dv_f=8.0; dv_c=20*5*0.05; dv_o=dv_deorbit(650)
dv_m=0.20*(dv_d+dv_f+dv_c+dv_o)
labels=["Drag\nmake-up","Formation\nkeeping","Collision\navoidance","Controlled\nde-orbit","Margin\n20%"]
vals=[dv_d,dv_f,dv_c,dv_o,dv_m]; dvT=sum(vals)
D["dvT"]=dvT; D["dv_deorbit"]=dv_o; D["dv_drag"]=dv_d
prop=lambda dv,isp,md=375.0: md*(np.exp(dv/(isp*G0))-1)
sysv=[("Cold gas\nIsp 70 s",70,"#9aa7b1"),("Hydrazine\nIsp 220 s",220,COOL),("Electric\nIsp 1500 s",1500,GOOD)]
fig=plt.figure(figsize=(9.4,4.8)); gs=gridspec.GridSpec(1,2,width_ratios=[1.3,1],wspace=0.34)
axL=fig.add_subplot(gs[0]); xb=np.arange(len(labels))
bars=axL.bar(xb,vals,color=[COOL,"#7fa8bd",WARN,BAD,"#cccccc"],width=0.7)
for b,v in zip(bars,vals): axL.text(b.get_x()+b.get_width()/2,v+1.5,f"{v:.0f}",ha="center",fontsize=8.3)
axL.set_xticks(xb); axL.set_xticklabels(labels,fontsize=8); axL.set_ylabel("Δv (m/s)"); axL.set_ylim(0,170)
axL.set_title(f"(a) Per-satellite Δv budget (≈{dvT:.0f} m/s, 5 yr)")
axL.text(0.03,0.96,"Controlled de-orbit dominates —\nthe 'permanent vs disposable' penalty",
         transform=axL.transAxes,ha="left",va="top",fontsize=8,color=BAD,
         bbox=dict(boxstyle="round,pad=0.4",fc="#fdecec",ec=BAD))
axR=fig.add_subplot(gs[1]); xs=np.arange(len(sysv))
pm=[prop(dvT,isp) for _,isp,_ in sysv]
axR.bar(xs,pm,color=[c for *_,c in sysv],width=0.62)
axR.set_xticks(xs); axR.set_xticklabels([s for s,_,_ in sysv],fontsize=8); axR.set_ylabel("Propellant mass (kg)")
axR.set_title("(b) Propellant for total Δv\n(375 kg dry bus)")
for i,v in enumerate(pm): axR.text(i,v+0.5,f"{v:.0f} kg",ha="center",fontsize=8.3)
D["prop_hydra"]=prop(dvT,220); D["prop_elec"]=prop(dvT,1500)
figtab(fig,"FIG. 5"); credit(fig,"Drag: NRLMSIS 2.1 density @650 km. De-orbit: Hohmann to 180 km perigee. Avoidance rate: Starlink FCC filing (144,404 maneuvers / 6 mo, H1-2025). Rocket equation.")
fig.savefig(OUT+"fig5_deltav.png"); plt.close(fig)

# ==========================================================================================
# Fig 6 : LAUNCH ECONOMICS (honest band)
# Falcon 9 customer ~$3,770/kg (reusable payload basis); Starship target $10 .. realistic $100-600
# ==========================================================================================
price=np.array([3770,1500,600,300,200,100,30]); mL=415.0; sats=81; hw=1.1e6
fig=plt.figure(figsize=(9.4,4.9)); gs=gridspec.GridSpec(1,2,width_ratios=[1.1,1],wspace=0.32)
axA=fig.add_subplot(gs[0])
axA.plot(price,price*mL/1e6,"o-",color=ACCENT,lw=2.3,label="launch cost / sat")
axA.plot(price,(hw+price*mL)/1e6,"s--",color=NAVY,lw=2.0,label="all-in / sat (hardware+launch)")
axA.set_xscale("log"); axA.invert_xaxis()
axA.axvspan(3770,3000,color="#ccc",alpha=0.25); axA.text(3770,1.3,"Falcon 9\ntoday",fontsize=7.6,color="#555",ha="center")
axA.axvspan(600,30,color=GOOD,alpha=0.08); axA.text(120,2.0,"Starship\ntarget band",fontsize=7.6,color=GOOD,ha="center")
axA.set_xlabel("Launch price ($/kg, log → cheaper)"); axA.set_ylabel("Cost per satellite ($M)")
axA.set_title("(a) Below ~$600/kg, hardware dominates"); axA.legend(fontsize=8)
axB=fig.add_subplot(gs[1])
era=["Shuttle\n(program avg)","Falcon 9\n(reusable)","Starship\n(realistic)","Starship\n(aspirational)"]
val=[54500,3770,300,30]
cols=[BAD,WARN,COOL,GOOD]
axB.bar(era,val,color=cols,width=0.62); axB.set_yscale("log"); axB.set_ylabel("$/kg to LEO (log)")
for i,v in enumerate(val): axB.text(i,v*1.15,f"${v:,}",ha="center",fontsize=8)
axB.set_title("(b) Launch $/kg trajectory")
axB.set_xticks(np.arange(len(era))); axB.set_xticklabels(era,fontsize=7.6)
figtab(fig,"FIG. 6"); credit(fig,"Falcon 9: SpaceX list $69.75M / 18,500 kg reusable. Starship: target band (analyst + Musk aspirational). Shuttle: program-averaged. Hardware $1.1M/sat (est.).")
fig.savefig(OUT+"fig6_launch_cost.png"); plt.close(fig)

# ==========================================================================================
# Fig 7 : SYSTEMS-LEVEL RISK MATRIX (executive)
# ==========================================================================================
fig,ax=plt.subplots(figsize=(8.8,6.0))
# 5x5 risk grid colouring
for i in range(5):
    for j in range(5):
        score=(i+1)*(j+1)
        c = GOOD if score<=4 else (WARN if score<=9 else (ACCENT if score<=14 else BAD))
        ax.add_patch(Rectangle((i,j),1,1,fc=c,ec="white",lw=2,alpha=0.30))
items=[ # (likelihood 0-4, consequence 0-4, label, marker color)
 (0.5,1.0,"Thermal:\nsingle node",GOOD),
 (2.0,2.4,"Thermal:\nMW-scale",WARN),
 (0.8,2.2,"Radiation\nTID",GOOD),
 (3.4,1.6,"Radiation\nSEU tax",WARN),
 (2.3,4.2,"Debris:\ncascade",BAD),
 (2.0,3.6,"Debris:\ncatastrophic",BAD),
 (2.5,3.0,"Formation\ncontrol",ACCENT),
 (3.6,2.2,"End-of-life\nde-orbit",ACCENT),
 (3.6,3.7,"Economics",BAD),
]
for lk,cq,lab,c in items:
    ax.scatter([lk],[cq],s=120,color=c,ec="white",lw=1.5,zorder=5)
    ax.annotate(lab,(lk,cq),xytext=(lk+0.10,cq+0.10),fontsize=7.8,color=NAVY,fontweight="bold")
ax.set_xlim(0,5); ax.set_ylim(0,5)
ax.set_xticks([0.5,1.5,2.5,3.5,4.5]); ax.set_xticklabels(["Very low","Low","Moderate","High","Very high"],fontsize=8)
ax.set_yticks([0.5,1.5,2.5,3.5,4.5]); ax.set_yticklabels(["Negligible","Minor","Moderate","Major","Catastrophic"],fontsize=8)
ax.set_xlabel("LIKELIHOOD →",fontweight="bold"); ax.set_ylabel("CONSEQUENCE →",fontweight="bold")
ax.set_title("Where the real risk lives: cooling is solved; debris, disposal & economics are not",fontsize=11)
ax.grid(False)
figtab(fig,"FIG. 7"); credit(fig,"Synthesis of Figs. 1-6 and Project Suncatcher (arXiv:2511.19468). Risk placement is the author's engineering judgement, anchored to the quantified findings.")
fig.savefig(OUT+"fig7_risk_matrix.png"); plt.close(fig)

# ==========================================================================================
print("="*78); print("REPORT II  (verified-data edition)  —  COMPUTED DIGEST"); print("="*78)
for k,v in D.items(): print(f"  {k:18s}: {v:,.2f}")
print("="*78); print("Figures ->",OUT)
