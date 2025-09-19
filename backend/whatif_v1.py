
"""
backend/whatif_v1.py

Simple what-if simulator: simulate a trainset failure and re-run optimizer.
"""
import os
import argparse
import pandas as pd
from optimization_run import run_optimization

def simulate_failure_and_optimize(trainsets_csv, failed_trainset_id, jobcards_csv=None, model_path=None, min_peak=18):
    df = pd.read_csv(trainsets_csv)
    if 'trainset_id' not in df.columns:
        # try to infer
        id_col = next((c for c in df.columns if 'train' in c.lower() and 'id' in c.lower()), None)
        if id_col is None:
            raise KeyError("trainset id column not found")
    else:
        id_col = 'trainset_id'
    # mark failed trainset by setting certificates to 0 and critical_jobs_open high OR remove it from pool
    df.loc[df[id_col].astype(str) == str(failed_trainset_id), 'certificate_valid'] = 0
    temp = trainsets_csv.replace(".csv", f".failed_{failed_trainset_id}.csv")
    df.to_csv(temp, index=False)
    res = run_optimization(trainset_csv=temp, jobcards_csv=jobcards_csv, model_path=model_path, min_peak_trainsets=min_peak)
    # cleanup temp
    try:
        os.remove(temp)
    except Exception:
        pass
    return res

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trainsets", required=True)
    parser.add_argument("--failed", required=True)
    parser.add_argument("--jobcards", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--min_peak", type=int, default=18)
    args = parser.parse_args()
    out = simulate_failure_and_optimize(args.trainsets, args.failed, jobcards_csv=args.jobcards, model_path=args.model, min_peak=args.min_peak)
    print("Status:", out["pulp_status"])
    print("Selected count:", len(out["selected_trainsets"]))
    print(out["details"].head(20).to_string(index=False))
