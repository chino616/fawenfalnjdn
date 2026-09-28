#!/usr/bin/env python3
"""Paper originals + actual reproduced arrays. Does NOT simulate or fabricate arrays.

Requires numpy matplotlib pymupdf pillow. Run --paper-only to extract source figures.
The figure reproductions require the grid files documented in README_CN.md.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import fitz
from PIL import Image, ImageOps, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))
COLORS = {'csi':'#bf438c','lar':'#e3a12a','joint':'#2463ad'}
LABELS = {'csi':'CsI 2021', 'lar':'LAr 2020', 'joint':'CsI + LAr'}


def sha256(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for b in iter(lambda:f.read(1<<20),b''): h.update(b)
    return h.hexdigest()


def source_figure(doc, number, out):
    """Locate a numbered paper caption; a human must inspect the exported crop.

    The v2 PDF may have a different physical page index from the journal PDF.
    This extractor searches caption variants rather than silently using a fixed index.
    """
    entry = CFG['figures'][str(number)]
    hints = [entry['page_index']] + [i for i in range(len(doc)) if i != entry['page_index']]
    patterns = [f'Figure {number}.', f'Figure {number}:',
                f'Fig. {number}:', f'FIG. {number}:', f'Fig. {number}.']
    page = None
    marks = []
    for index in hints:
        candidate = doc.load_page(index)
        matches = []
        for pattern in patterns:
            matches = candidate.search_for(pattern)
            if matches:
                break
        if matches:
            page, marks = candidate, matches
            print(f'Figure {number}: caption on actual PDF page {index + 1}; verify export crop manually.')
            break
    if page is None:
        raise RuntimeError(f'Figure {number} caption not found in supplied PDF. Check text layer and exact paper version.')
    # Conservative page-top-to-caption extraction. May contain preceding prose;
    # do not use for pixel-based contour comparison until crop bbox is audited.
    bottom = min(page.rect.y1, max(x.y1 for x in marks) + 28)
    clip = fitz.Rect(page.rect.x0 + 14, page.rect.y0 + 14, page.rect.x1 - 14, bottom)
    pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), clip=clip, alpha=False)
    pix.save(out)


def load_npz(file, dims):
    if not file.is_file(): raise FileNotFoundError(f'Missing REAL model output: {file}')
    with np.load(file, allow_pickle=False) as z:
        required=('x','y' if dims==2 else 'x','chi2_csi','chi2_lar')
        if dims==1: required=('x','chi2_csi','chi2_lar')
        for key in required:
            if key not in z: raise ValueError(f'{file}: missing {key}')
        d={k:np.asarray(z[k],dtype=float) for k in z.files}
    if d['x'].ndim!=1 or len(d['x'])<3 or not np.all(np.diff(d['x'])>0):
        raise ValueError(f'{file}: x must be an increasing 1D array')
    if dims==2:
        if d['y'].ndim!=1 or len(d['y'])<3 or not np.all(np.diff(d['y'])>0):
            raise ValueError(f'{file}: y must be an increasing 1D array')
        expect=(len(d['y']),len(d['x']))
    else: expect=(len(d['x']),)
    for k in ('chi2_csi','chi2_lar'):
        if d[k].shape!=expect or not np.all(np.isfinite(d[k])):
            raise ValueError(f'{file}: {k} shape must be {expect}, with finite RAW profiled chi2')
    if 'chi2_joint' in d:
        if d['chi2_joint'].shape!=expect or not np.all(np.isfinite(d['chi2_joint'])):
            raise ValueError(f'{file}: chi2_joint shape must be {expect} and finite')
    else:
        d['chi2_joint']=d['chi2_csi']+d['chi2_lar']
    return d


def dchi(d, who):
    a=d['chi2_'+who]
    return a-a.min()


def contour(ax,d,who,filled=True):
    v=dchi(d,who)
    X,Y=np.meshgrid(d['x'],d['y'])
    threshold=CFG['confidence_2d']
    if v.min()<=threshold and v.max()>threshold:
        if filled: ax.contourf(X,Y,v,levels=[-1e-6,threshold],colors=[COLORS[who]],alpha=.17)
        ax.contour(X,Y,v,levels=[threshold],colors=[COLORS[who]],linewidths=1.8)
    elif v.max()<=threshold:
        ax.text(.5,.97,who+' region extends beyond frame',transform=ax.transAxes,ha='center',va='top',fontsize=7)
    else: raise ValueError('Invalid delta chi2')


def format_plane(ax,spec):
    ax.set_xlabel(spec['x']); ax.set_ylabel(spec['y']);
    if 'xlim' in spec: ax.set_xlim(*spec['xlim'])
    if 'ylim' in spec: ax.set_ylim(*spec['ylim'])
    ax.grid(alpha=.15)


def plot_fig_3to6(number, indir, out):
    cfg=CFG['figures'][str(number)]
    fig,axs=plt.subplots(2,2,figsize=(11,9),layout='constrained')
    for r,spec in enumerate(cfg['rows']):
        file=indir/f'fig{number}_{spec["id"]}.npz'
        d=load_npz(file,2)
        for who in ('csi','lar'): contour(axs[r,0],d,who)
        contour(axs[r,1],d,'joint')
        for col in (0,1): format_plane(axs[r,col],spec)
        axs[r,0].set_title(f'{spec["id"]}: separate CsI / LAr')
        axs[r,1].set_title(f'{spec["id"]}: joint CsI + LAr')
        for who in ('csi','lar'):
            axs[r,0].plot([],[],c=COLORS[who],label=LABELS[who])
        axs[r,0].legend(fontsize=8,loc='upper right')
        axs[r,1].plot([],[],c=COLORS['joint'],label=LABELS['joint'])
        axs[r,1].legend(fontsize=8,loc='upper right')
    fig.suptitle(f'REPRODUCED FROM SUPPLIED NUMERIC ARRAYS | Fig. {number} | {cfg["title"]}\n90% CL (2 dof); NOT paper data digitization',fontsize=12)
    f=out/f'Fig{number:02d}_reproduction.png'; fig.savefig(f,dpi=190)
    fig.savefig(out/f'Fig{number:02d}_reproduction.pdf')
    plt.close(fig)
    return f


def plot_fig7(indir,out):
    c=CFG['figures']['7']; fig,axs=plt.subplots(2,3,figsize=(14,8),layout='constrained')
    for j,spec in enumerate(c['profiles']):
        d=load_npz(indir/f'fig7_profile_{spec["id"]}.npz',1)
        for who in ('csi','lar','joint'):
            axs[0,j].plot(d['x'],dchi(d,who),c=COLORS[who],lw=1.8,label=LABELS[who])
        axs[0,j].set(xlabel=spec['x'],ylabel=r'$\Delta\chi^2$',title=spec['id'].capitalize())
        axs[0,j].grid(alpha=.2)
        if j==0: axs[0,j].legend(fontsize=8)
    for j,spec in enumerate(c['planes']):
        d=load_npz(indir/f'fig7_plane_{spec["id"]}.npz',2)
        for who in ('csi','lar','joint'): contour(axs[1,j],d,who,filled=False)
        format_plane(axs[1,j],spec)
        axs[1,j].set_title(spec['id'].replace('_','-')+' | 90% CL (2 dof)')
    fig.suptitle('REPRODUCED FROM SUPPLIED NUMERIC ARRAYS | Fig. 7 | NGI',fontsize=12)
    f=out/'Fig07_reproduction.png'; fig.savefig(f,dpi=190)
    fig.savefig(out/'Fig07_reproduction.pdf')
    plt.close(fig)
    return f


def compare_images(original,repro,target):
    im1=Image.open(original).convert('RGB'); im2=Image.open(repro).convert('RGB')
    # Images are not overlaid or re-digitized: simply side-by-side with explicit provenance.
    H=1450; W=1100; gap=36; head=65
    def fit(im):
        im.thumbnail((W,H),Image.Resampling.LANCZOS)
        return im
    im1=fit(im1); im2=fit(im2)
    canvas=Image.new('RGB',(2*W+gap,H+head),'white'); dr=ImageDraw.Draw(canvas)
    dr.text((10,15),'PAPER ORIGINAL (PDF FIGURE)',fill='black')
    dr.text((W+gap+10,15),'NUMERICAL REPRODUCTION (FROM SUPPLIED NPZ)',fill='black')
    canvas.paste(im1,((W-im1.width)//2,head+(H-im1.height)//2))
    canvas.paste(im2,(W+gap+(W-im2.width)//2,head+(H-im2.height)//2))
    canvas.save(target)
    return canvas


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--paper-pdf',type=Path,required=True)
    p.add_argument('--grids',type=Path,default=None,help='Actual raw-profiled chi2 .npz files')
    p.add_argument('--out',type=Path,default=HERE/'output')
    p.add_argument('--paper-only',action='store_true')
    a=p.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
    if not a.paper_pdf.is_file(): p.error('Paper PDF unavailable. A Windows file:/// URL is not accessible from a different computer.')
    document=fitz.open(a.paper_pdf)
    if len(document)<=22: p.error('Unexpected paper PDF length; needs 2211.11905v2 (43 pages).')
    provenance={'paper_path':str(a.paper_pdf),'paper_sha256':sha256(a.paper_pdf),'paper_pages':len(document),'mode':'paper-only' if a.paper_only else 'paper+real-grids','grids':{}}
    for n in range(3,8):
        source_figure(document,n,a.out/f'Fig{n:02d}_original.png')
    if a.paper_only:
        print('Source figures extracted: '+str(a.out))
    else:
        if a.grids is None or not a.grids.is_dir(): p.error('Use --grids PATH with 14 real NPZ arrays (see README_CN).')
        for n in range(3,7): plot_fig_3to6(n,a.grids,a.out)
        plot_fig7(a.grids,a.out)
        for file in sorted(a.grids.glob('fig*.npz')): provenance['grids'][file.name]=sha256(file)
        assembled=[]
        for n in range(3,8):
            assembled.append(compare_images(a.out/f'Fig{n:02d}_original.png',a.out/f'Fig{n:02d}_reproduction.png',a.out/f'Fig{n:02d}_comparison.png').convert('RGB'))
        assembled[0].save(a.out/'Fig03_to_Fig07_comparison.pdf',save_all=True,append_images=assembled[1:],resolution=150)
        print('Original, reproduced, comparison files written to '+str(a.out))
    (a.out/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__': main()
