#!/usr/bin/env python3
"""Minier dimensionality research harness.

Two deliberately separate experiments share one audit philosophy:
(1) zeta-zero spectral concentration must beat matched/null controls;
(2) EEG features must survive participant-level validation and dimensionality sweeps.

This code does not assert a Riemann-Hypothesis proof or an Alzheimer diagnostic.
"""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd


def gini(x):
    x=np.abs(np.asarray(x,float).ravel())
    if not np.any(x): return 0.0
    x=np.sort(x); n=len(x)
    return float((2*np.sum((np.arange(n)+1)*x)/(n*np.sum(x)))-(n+1)/n)


def concentration(x, top_frac=.01):
    p=np.abs(np.asarray(x,float).ravel())**2
    p=p/(p.sum()+1e-30); k=max(1,int(math.ceil(len(p)*top_frac)))
    q=np.sort(p)[::-1]
    ent=float(-(p*np.log(p+1e-30)).sum())
    return {"top_ratio":float(q[:k].sum()),"gini":gini(p),"entropy":ent,
            "effective_support":float(np.exp(ent))}


def zeta_experiment(nzeros:int, seed:int, out:Path):
    import mpmath as mp
    mp.mp.dps=50
    t=np.array([float(mp.im(mp.zetazero(k))) for k in range(1,nzeros+1)])
    # Put zero ordinates onto a fixed grid, then compare parameterized phase views.
    W=1
    while W < 64*nzeros: W*=2
    grid=np.zeros(W)
    idx=np.floor((t-t.min())/(t.max()-t.min()+1e-30)*(W-1)).astype(int)
    np.add.at(grid,idx,1.0)
    base=np.abs(np.fft.rfft(grid))
    constants={"basel":math.pi**2/6,"silver":1+math.sqrt(2),"golden":(1+math.sqrt(5))/2,
               "sqrt2":math.sqrt(2),"control4":4.0}
    rows=[]
    k=np.arange(len(base),dtype=float)
    for name,a in constants.items():
        # Equal-energy modulation: candidate labels change phase/spacing, not total gain.
        mod=np.abs(np.fft.rfft(grid*np.cos(2*np.pi*a*np.arange(W)/W)))
        c=concentration(mod)
        rows.append({"name":name,"alpha":a,**c})
    rng=np.random.default_rng(seed)
    for j in range(32):
        a=float(rng.uniform(1.0,4.0))
        mod=np.abs(np.fft.rfft(grid*np.cos(2*np.pi*a*np.arange(W)/W)))
        rows.append({"name":f"random_{j:02d}","alpha":a,**concentration(mod)})
    out.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(rows).to_csv(out/"zeta_concentration.csv",index=False)
    np.savetxt(out/"zeta_zero_ordinates.txt",t,fmt="%.17g")
    (out/"run.json").write_text(json.dumps({"experiment":"zeta","nzeros":nzeros,"seed":seed,"grid":W},indent=2))
    print(pd.DataFrame(rows).sort_values("top_ratio",ascending=False).head(12).to_string(index=False))


def find_set_files(root:Path):
    # Prefer official preprocessed derivatives when present.
    files=sorted((root/"derivatives").glob("sub-*/eeg/*.set")) if (root/"derivatives").exists() else []
    if not files: files=sorted(root.glob("sub-*/eeg/*.set"))
    return files


def load_groups(root:Path):
    p=pd.read_csv(root/"participants.tsv",sep="\t")
    # Upstream commonly uses Group A/F/C; tolerate common column spellings.
    cols={c.lower():c for c in p.columns}
    idc=cols.get("participant_id"); gc=cols.get("group")
    if not idc or not gc: raise RuntimeError("participants.tsv needs participant_id and Group/group")
    return dict(zip(p[idc].astype(str),p[gc].astype(str)))


def band_features(signal,sfreq):
    from scipy.signal import welch
    f,p=welch(signal,fs=sfreq,nperseg=min(len(signal),int(sfreq*4)))
    bands={"delta":(1,4),"theta":(4,8),"alpha":(8,13),"beta":(13,30),"gamma":(30,45)}
    total=np.trapz(p[(f>=1)&(f<=45)],f[(f>=1)&(f<=45)])+1e-30
    feat={}
    for n,(lo,hi) in bands.items():
        m=(f>=lo)&(f<hi); feat[f"fft_{n}"]=float(np.trapz(p[m],f[m])/total)
    # Auditable experimental phase-warp family. These are candidate representations,
    # not claims that metallic constants are biological constants.
    alphas={"golden":(1+math.sqrt(5))/2,"silver":1+math.sqrt(2),"sqrt2":math.sqrt(2),"control4":4.0}
    x=np.asarray(signal,float); n=np.arange(len(x))
    for name,a in alphas.items():
        y=x*np.cos(2*np.pi*(a-1.0)*n/len(x))
        fy,py=welch(y,fs=sfreq,nperseg=min(len(y),int(sfreq*4)))
        q=py[(fy>=1)&(fy<=45)]; q=q/(q.sum()+1e-30)
        feat[f"{name}_gini"]=gini(q)
        feat[f"{name}_top1pct"]=float(np.sort(q)[::-1][:max(1,len(q)//100)].sum())
    return feat


def eeg_table(root:Path, channel:str):
    import mne
    groups=load_groups(root); rows=[]
    for fn in find_set_files(root):
        sid=next((p for p in fn.parts if p.startswith("sub-")),None)
        if sid not in groups: continue
        raw=mne.io.read_raw_eeglab(fn,preload=True,verbose="ERROR")
        if channel not in raw.ch_names: continue
        x=raw.get_data(picks=[channel])[0]
        # One participant -> one feature row. Avoid epoch-as-person leakage.
        feat=band_features(x,float(raw.info["sfreq"]))
        rows.append({"participant_id":sid,"group":groups[sid],**feat})
    return pd.DataFrame(rows)


def cv_dimension_sweep(df, ga, gb, seed, out):
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.feature_selection import SelectKBest, f_classif
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold, cross_validate
    from sklearn.metrics import make_scorer, balanced_accuracy_score
    d=df[df.group.isin([ga,gb])].copy()
    y=(d.group==ga).astype(int).to_numpy()
    feature_cols=[c for c in d.columns if c not in ("participant_id","group")]
    X=d[feature_cols].replace([np.inf,-np.inf],np.nan).fillna(0).to_numpy()
    if len(np.unique(y))<2: raise RuntimeError("Need both requested groups")
    folds=min(5,int(np.bincount(y).min()))
    cv=StratifiedKFold(folds,shuffle=True,random_state=seed)
    dims=sorted(set([2,4,8,12,16,24,32,len(feature_cols)]))
    dims=[k for k in dims if 1<=k<=len(feature_cols)]
    rows=[]
    for k in dims:
        pipe=Pipeline([("scale",StandardScaler()),("select",SelectKBest(f_classif,k=k)),
                       ("clf",LogisticRegression(max_iter=5000,class_weight="balanced"))])
        s=cross_validate(pipe,X,y,cv=cv,scoring={"acc":"accuracy","bal":make_scorer(balanced_accuracy_score),"auc":"roc_auc"})
        rows.append({"k":k,"accuracy":float(s["test_acc"].mean()),"balanced_accuracy":float(s["test_bal"].mean()),"auc":float(s["test_auc"].mean()),"auc_sd":float(s["test_auc"].std())})
    out.mkdir(parents=True,exist_ok=True)
    d.to_csv(out/"subject_features.csv",index=False)
    pd.DataFrame(rows).to_csv(out/"dimension_sweep.csv",index=False)
    (out/"run.json").write_text(json.dumps({"experiment":"eeg","groups":[ga,gb],"seed":seed,"subjects":len(d),"features":feature_cols},indent=2))
    print(pd.DataFrame(rows).to_string(index=False))


def main():
    ap=argparse.ArgumentParser(); sub=ap.add_subparsers(dest="cmd",required=True)
    z=sub.add_parser("zeta"); z.add_argument("--zeros",type=int,default=109); z.add_argument("--seed",type=int,default=20260911); z.add_argument("--out",type=Path,default=Path("results/zeta"))
    e=sub.add_parser("eeg"); e.add_argument("--bids-root",type=Path,required=True); e.add_argument("--group-a",default="A"); e.add_argument("--group-b",default="C"); e.add_argument("--channel",default="Pz"); e.add_argument("--seed",type=int,default=20260911); e.add_argument("--out",type=Path,default=Path("results/eeg"))
    a=ap.parse_args()
    if a.cmd=="zeta": zeta_experiment(a.zeros,a.seed,a.out)
    else: cv_dimension_sweep(eeg_table(a.bids_root,a.channel),a.group_a,a.group_b,a.seed,a.out)
if __name__=="__main__": main()
