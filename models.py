import os
import pandas as pd
import numpy as np
import statsmodels.api as sm

FILE_PATH  = r"C:\Users\Valentín\OneDrive\Documentos\IE\TFGs\TFG Data\data\DATABASE_1.xlsx"
OUTPUT_DIR = "regression_outputs(copia)"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Load & prepare ────────────────────────────────────────────────────────────
df = pd.read_excel(FILE_PATH)
df["Position"] = df["Position"].astype(str).str.upper().str.strip()
df = df[df["Position"] != "GK"].copy()
df = df[df["Minutes played"] >= 1000].copy()

# Position dummies — reference category: MF
df["DF"] = (df["Position"] == "DF").astype(float)
df["FW"] = (df["Position"] == "FW").astype(float)

numeric_cols = [
    "CV_Rating", "Minutes played", "Gap_Easy_vs_Difficult", "DF", "FW",
    "T+I_90_mean",       "CV_T+I_90",
    "Clearances_90_mean","CV_Clearances_90",
    "PassAcc%_mean",     "CV_PassAcc%",
    "KeyPass_90_mean",   "CV_KeyPass_90",
    "SoT_90_mean",       "CV_SoT_90",
    "xG_90_mean",        "CV_xG_90",
]
for c in numeric_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# Positional subsets
df_def = df[df["Position"] == "DF"].copy()
df_mf  = df[df["Position"] == "MF"].copy()
df_fw  = df[df["Position"] == "FW"].copy()

print(f"Full sample n={len(df)} | DF n={len(df_def)} | MF n={len(df_mf)} | FW n={len(df_fw)}\n")

# ── OLS helper ────────────────────────────────────────────────────────────────
all_models   = []
coef_records = []
beta_records = []

def run_ols(label, y_col, x_cols, data=None):
    src = data if data is not None else df
    d = src[[y_col] + x_cols].dropna()
    n = len(d)
    if n < max(20, len(x_cols) * 8):
        print(f"⚠  {label}: n={n} — insufficient observations. Skipped.")
        return None

    y = d[y_col]
    X = sm.add_constant(d[x_cols])
    m = sm.OLS(y, X).fit()
    all_models.append((label, m))

    # Raw coefficients
    for v in m.params.index:
        coef_records.append({
            "model":   label,
            "variable": v,
            "coef":    round(m.params[v], 6),
            "std_err": round(m.bse[v], 6),
            "t":       round(m.tvalues[v], 4),
            "p_value": round(m.pvalues[v], 6),
            "n":       int(m.nobs),
            "R2":      round(m.rsquared, 4),
            "adj_R2":  round(m.rsquared_adj, 4),
        })

    # Standardised betas
    d_z = (d - d.mean()) / d.std()
    mz  = sm.OLS(d_z[y_col], sm.add_constant(d_z[x_cols])).fit()
    for v in mz.params.index:
        beta_records.append({
            "model":    label + " (std)",
            "variable": v,
            "beta_std": round(mz.params[v], 4),
            "p_value":  round(mz.pvalues[v], 6),
            "n":        int(mz.nobs),
            "R2":       round(mz.rsquared, 4),
            "adj_R2":   round(mz.rsquared_adj, 4),
        })
    return m

# ── GROUP A ───────────────────────────────────────────────────────────────────
run_ols("A1 — Structural baseline",
        y_col  = "CV_Rating",
        x_cols = ["Minutes played", "DF", "FW"])

run_ols("A2 — + Opponent sensitivity (Gap)",
        y_col  = "CV_Rating",
        x_cols = ["Minutes played", "Gap_Easy_vs_Difficult", "DF", "FW"])

# ── GROUP B ───────────────────────────────────────────────────────────────────
run_ols("DF1 — T+I mean → CV_T+I",
        y_col  = "CV_T+I_90",
        x_cols = ["T+I_90_mean", "Minutes played"],
        data   = df_def)

run_ols("DF2 — Clearances mean → CV_Clearances",
        y_col  = "CV_Clearances_90",
        x_cols = ["Clearances_90_mean", "Minutes played"],
        data   = df_def)

run_ols("MF1 — PassAcc mean → CV_PassAcc",
        y_col  = "CV_PassAcc%",
        x_cols = ["PassAcc%_mean", "Minutes played"],
        data   = df_mf)

run_ols("MF2 — KeyPass mean → CV_KeyPass",
        y_col  = "CV_KeyPass_90",
        x_cols = ["KeyPass_90_mean", "Minutes played"],
        data   = df_mf)

run_ols("FW1 — SoT mean → CV_SoT  [LIMITED n=47]",
        y_col  = "CV_SoT_90",
        x_cols = ["SoT_90_mean", "Minutes played"],
        data   = df_fw)

run_ols("FW2 — xG mean → CV_xG  [LIMITED n=47]",
        y_col  = "CV_xG_90",
        x_cols = ["xG_90_mean", "Minutes played"],
        data   = df_fw)

# ── Console summary ────────────────────────────────────────────────────────────
print("=" * 68)
print(f"  {'Model':<44} {'n':>4}  {'R²':>6}  {'Adj.R²':>7}")
print("-" * 68)
for label, m in all_models:
    print(f"  {label:<44} {int(m.nobs):>4}  {m.rsquared:>6.3f}  {m.rsquared_adj:>7.3f}")

# ── Save outputs ───────────────────────────────────────────────────────────────
txt_path = os.path.join(OUTPUT_DIR, "summaries.txt")
with open(txt_path, "w", encoding="utf-8") as f:
    for label, m in all_models:
        f.write(f"\n{'='*80}\nMODEL: {label}\n{'='*80}\n")
        f.write(m.summary().as_text())
        f.write("\n")
print(f"\nSummaries  → {txt_path}")

compare = [{"Model": lbl, "n": int(m.nobs),
            "R2": round(m.rsquared, 4),
            "Adj_R2": round(m.rsquared_adj, 4),
            "F_pvalue": round(m.f_pvalue, 6)}
           for lbl, m in all_models]

xlsx_path = os.path.join(OUTPUT_DIR, "coefficients.xlsx")
with pd.ExcelWriter(xlsx_path, engine="openpyxl") as w:
    pd.DataFrame(compare).to_excel(w, index=False, sheet_name="model_comparison")
    pd.DataFrame(coef_records).to_excel(w, index=False, sheet_name="coefficients_raw")
    pd.DataFrame(beta_records).to_excel(w, index=False, sheet_name="betas_standardised")
print(f"Coefficients → {xlsx_path}\n✅ Done.")