#!/usr/bin/env python3
"""Build the explicit CONUS+ reproduction spectrum from bundled Daya Bay data.

Implements Daya Bay arXiv:2102.04614 Eq. (8) for the central region. This is a
reproduction approximation, not a collaboration data release.
"""
from __future__ import annotations
import csv, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DB={"U235":0.564,"U238":0.076,"Pu239":0.304,"Pu241":0.056}
KKL={"U235":0.53,"U238":0.08,"Pu239":0.32,"Pu241":0.07}
U238=[4.833,-4.616,1.988,-0.4828,0.05576,-0.002091]
PU241=[2.990,-2.882,1.278,-0.3343,0.03905,-0.001754]
def model(E,c): return math.exp(sum(a*E**i for i,a in enumerate(c)))
def read(name):
    with (ROOT/'data/external/dayabay'/name).open() as f:return list(csv.DictReader(f))
def main():
    u,pc,t=read('dayabay_u235_unfolded.csv'),read('dayabay_pu_combo_unfolded.csv'),read('dayabay_total_unfolded.csv')
    d={k:KKL[k]-DB[k] for k in DB}; rows=[]
    for a,b,c in zip(u,pc,t):
        E=float(a['energy_mev']); s235=float(a['spectrum_without_ibd_per_fission_per_mev']); sc=float(b['spectrum_without_ibd_per_fission_per_mev']); st=float(c['spectrum_without_ibd_per_fission_per_mev'])
        pred=st+d['U235']*s235+d['Pu239']*sc+d['U238']*model(E,U238)+(d['Pu241']-0.183*d['Pu239'])*model(E,PU241)
        if E<=7.675: rows.append([E,pred,st,pred/st,'dayabay_eq8_kkl_adjustment'])
    ratio=rows[-1][3]
    for r in read('dayabay_high_energy.csv'):
        E=float(r['energy_mev'])
        if E>7.675:
            st=float(r['spectrum_without_ibd_per_fission_per_mev']); rows.append([E,st*ratio,st,ratio,'dayabay_high_energy_constant_kkl_ratio'])
    rows.sort(); area=sum((b[0]-a[0])*(a[1]+b[1])/2 for a,b in zip(rows,rows[1:]))
    out=ROOT/'data/conus_plus_2025_reproduction/reactor_spectrum_shape.csv'
    with out.open('w',newline='') as f:
        w=csv.writer(f); w.writerow(['energy_mev','spectrum_per_fission_per_mev','normalized_shape_per_mev','unadjusted_dayabay_total_per_fission_per_mev','kkl_to_dayabay_ratio','construction_status'])
        for E,p,st,r,status in rows:w.writerow([E,p,p/area,st,r,status])
if __name__=='__main__':main()
