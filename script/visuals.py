import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Set up
FILE_PATH = r"C:\Users\Valentín\OneDrive\Documentos\IE\TFGs\TFG Data\data\DATABASE_1.xlsx"     
OUTPUT_DIR = "figuras_tfg_final"
os.makedirs(OUTPUT_DIR, exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams["savefig.dpi"] = 300

TOP_K = 15         
TABLE_N = 15        
MIN_N_MATCHES = 5   # minimum games

def savefig(filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    print(f"Figure saved: {path}")

# Load
df = pd.read_excel(FILE_PATH)

# Check and filters
required = ["Name", "Team", "Position", "Age", "Minutes played", "CV_Rating"]
missing = [c for c in required if c not in df.columns]
if missing:
    raise ValueError(f"Faltan columnas necesarias: {missing}")

df["Position"] = df["Position"].astype(str).str.strip().str.upper()

# Clean NaNs 
df = df.dropna(subset=["Name","Team","Position","Age","Minutes played","CV_Rating"]).copy()

print(f"Dataset ready: {len(df)} players")
print(f"exit: {OUTPUT_DIR}")

# Visual 1 and 2: TOP 15 (CV_Rating)
top_consistent = df.sort_values("CV_Rating", ascending=True).head(TOP_K).copy()
top_inconsistent = df.sort_values("CV_Rating", ascending=False).head(TOP_K).copy()

plt.figure(figsize=(10, 7))
sns.barplot(data=top_consistent, y="Name", x="CV_Rating")
plt.title(f"Top {TOP_K} MOST Consistent players (Lower CV Rating)")
plt.xlabel("CV Rating (%)")
plt.ylabel("")
savefig("01_top15_most_consistent.png")
plt.show()

plt.figure(figsize=(10, 7))
sns.barplot(data=top_inconsistent, y="Name", x="CV_Rating")
plt.title(f"Top {TOP_K} LEAST Consistent players (Higher CV Rating)")
plt.xlabel("CV Rating (%)")
plt.ylabel("")
savefig("02_top15_least_consistent.png")
plt.show()

# Visual 3: Histogram 
plt.figure(figsize=(9,6))
sns.histplot(df["CV_Rating"], bins=20, kde=True)
plt.title("CV Rating Distribution")
plt.xlabel("CV Rating (%)")
plt.ylabel("Number of players")
savefig("03_histogram_cv_rating.png")
plt.show()

# Visual 4: Consistency per position (CV_Rating)
plt.figure(figsize=(8.5, 5.5))
sns.violinplot(data=df, x="Position", y="CV_Rating", inner="box")
plt.title("Consistency Rating per Position")
plt.xlabel("Position")
plt.ylabel("CV Rating (%)")
savefig("04_cv_per_position.png")
plt.show()

# Visual 5: Age vs CV_Rating + tendency
plt.figure(figsize=(9, 6))
sns.regplot(
    data=df, x="Age", y="CV_Rating",
    scatter_kws={"alpha": 0.55},
    line_kws={"linewidth": 2}
)
plt.title("Age vs Consistency (CV Rating)")
plt.xlabel("Age")
plt.ylabel("CV Rating (%)")
savefig("05_age_vs_cv_rating.png")
plt.show()

# Visual 6: Minutes vs CV_Rating + tendency
plt.figure(figsize=(9, 6))
sns.regplot(
    data=df, x="Minutes played", y="CV_Rating",
    scatter_kws={"alpha": 0.55},
    line_kws={"linewidth": 2}
)
plt.title("Minutes played vs Consistency (CV Rating)")
plt.xlabel("Minutes played")
plt.ylabel("CV Rating (%)")
savefig("06_minutes_vs_cv_rating.png")
plt.show()

# Visual 7, 8 and 9: 3 Tables: Most inconsitency per rival difficulty 
# We need
# - CV_Rating_Easy, Rating_Easy_n
# - CV_Rating_Medium, Rating_Medium_n
# - CV_Rating_Difficult, Rating_Difficult_n

def make_table(cv_col, n_col, title, filename):
    # Checks
    needed = ["Name", "Team", cv_col, n_col]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        print(f"'{title}'. missing columns: {missing}")
        return

    # Filter: minimum number of matches
    tmp = df.copy()
    tmp[n_col] = tmp[n_col].fillna(0)
    tmp = tmp[tmp[n_col] >= MIN_N_MATCHES].copy()

    if tmp.empty:
        print(f"'{title}' empty: ")
        return

    # Top N most inconsistent
    tmp = tmp.sort_values(cv_col, ascending=False).head(TABLE_N)

    # Only columns 
    tmp = tmp[["Name", "Team", cv_col]].copy()

    # CV Format
    tmp[cv_col] = tmp[cv_col].astype(float).map(lambda x: f"{x:.2f}%")

    tmp = tmp.rename(columns={cv_col: "CV"}).reset_index(drop=True)

    # Table as a figure
    fig_h = max(3.5, 0.45 * (len(tmp) + 1))  
    fig, ax = plt.subplots(figsize=(10, fig_h))
    ax.axis("off")
    ax.set_title(title, fontsize=12, pad=12)

    table = ax.table(
        cellText=tmp.values,
        colLabels=tmp.columns,
        cellLoc="center",
        loc="center"
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.15, 1.2)

    # Save
    out_path = os.path.join(OUTPUT_DIR, filename)
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Table saved: {out_path}")

    plt.show()

make_table("CV_Rating_Easy","Rating_Easy_n",
           "Top Inconsistent in Easy Matches",
           "07_tabla_cv_facil.png")

make_table("CV_Rating_Medium","Rating_Medium_n",
           "Top Inconsistent in Medium Matches",
           "08_tabla_cv_medio.png")

make_table("CV_Rating_Difficult","Rating_Difficult_n",
           "Top Inconsistent in Difficult Matches",
           "09_tabla_cv_dificil.png")

# Visual 10: Classification REAL vs based on consistency

# 1. Consistency per team (weighted by minutes)
team_consistency = (
    df.dropna(subset=["Team", "CV_Rating", "Minutes played"])
      .groupby("Team")
      .apply(lambda x: np.average(x["CV_Rating"], weights=x["Minutes played"]))
      .reset_index(name="Team_CV")
)

team_consistency = team_consistency.sort_values("Team_CV").reset_index(drop=True)
team_consistency["Position_consistency"] = team_consistency.index + 1

# 2. Real classification
real_order = [
    "Barcelona",
    "Real Madrid",
    "Atletico Madrid",
    "Athletic Club",
    "Villarreal",
    "Betis",
    "Celta",
    "Rayo Vallecano",
    "Osasuna",
    "Mallorca",
    "Real Sociedad",
    "Valencia",
    "Getafe",
    "Espanyol",
    "Alaves",
    "Girona",
    "Sevilla",
    "Leganes",
    "Las Palmas",
    "Valladolid",
]

league_table = pd.DataFrame({
    "Team": real_order,
    "Position_real": list(range(1, len(real_order) + 1))
})

# 3. Merge
team_analysis = pd.merge(league_table, team_consistency, on="Team", how="left")

missing = team_analysis[team_analysis["Team_CV"].isna()]["Team"].tolist()
if missing:
    print("⚠️ ")
    for t in missing:
        print(" -", t)

# 4. Tables
real_sorted = team_analysis.sort_values("Position_real")[["Position_real", "Team"]].copy()

cons_sorted = team_analysis.sort_values("Position_consistency")[["Position_consistency", "Team", "Team_CV"]].copy()
cons_sorted["Team_CV"] = cons_sorted["Team_CV"].map(lambda x: f"{x:.2f}%")

# 5. Figure with 2 tables
fig, axes = plt.subplots(1, 2, figsize=(16, 8))

axes[0].axis("off")
axes[0].set_title("Real Classification 24/25", fontsize=12, pad=12)
t1 = axes[0].table(
    cellText=real_sorted.values,
    colLabels=real_sorted.columns,
    cellLoc="center",
    loc="center"
)
t1.auto_set_font_size(False)
t1.set_fontsize(10)
t1.scale(1, 1.2)

axes[1].axis("off")
axes[1].set_title("Classification based on Consistency (team CV)", fontsize=12, pad=12)
t2 = axes[1].table(
    cellText=cons_sorted.values,
    colLabels=cons_sorted.columns,
    cellLoc="center",
    loc="center"
)
t2.auto_set_font_size(False)
t2.set_fontsize(10)
t2.scale(1, 1.2)

out_path = os.path.join(OUTPUT_DIR, "10_clasificacion_real_vs_consistencia.png")
fig.savefig(out_path, dpi=300, bbox_inches="tight")
print(f"Saved{out_path}")
plt.show()

# Visual 11, 12 and 13: Specific metrics per position
# DF: T+I | MF: Pass Accuracy | FW: xG

TOP_N_METRIC = 15

def scatter_topN_metric_by_position(
    data,
    position,
    x_mean_col,
    y_cv_col,
    title,
    xlabel,
    ylabel,
    filename,
    top_n=15,
    invert_y=True
):
    # Checks columns
    needed = ["Name", "Team", "Position", x_mean_col, y_cv_col]
    missing = [c for c in needed if c not in data.columns]
    if missing:
        print(f"⚠️")
        return

    # Filter per position + NaNs
    tmp = data.copy()
    tmp["Position"] = tmp["Position"].astype(str).str.upper().str.strip()
    tmp = tmp[tmp["Position"] == position].dropna(subset=[x_mean_col, y_cv_col, "Name", "Team"]).copy()

    if tmp.empty:
        print(f"⚠️ ")
        return

    # Top N (higher = best / bigger volume)
    tmp = tmp.sort_values(x_mean_col, ascending=False).head(top_n).copy()

    # Plot
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=tmp, x=x_mean_col, y=y_cv_col, s=90, alpha=0.85)

    # Labels (names)
    for _, r in tmp.iterrows():
        plt.annotate(
            r["Name"],
            (r[x_mean_col], r[y_cv_col]),
            fontsize=9,
            xytext=(6, 4),
            textcoords="offset points"
        )

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    # Lower CV = more consistent 
    if invert_y:
        plt.gca().invert_yaxis()

    # Save
    out_path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    print(f"Saved {out_path}")
    plt.show()


# 1) DF — Tackles + Interceptions
scatter_topN_metric_by_position(
    df,
    position="DF",
    x_mean_col="T+I_90_mean",
    y_cv_col="CV_T+I_90",
    title=f"DF (Top {TOP_N_METRIC} in T+I/90): Performance vs Consistency",
    xlabel="Tackles + Interceptions per 90 min (mean)",
    ylabel="CV T+I per 90 min (%)",
    filename="11_DF_TI_mean_vs_CV_TI_top15.png",
    top_n=TOP_N_METRIC,
    invert_y=True
)

# 2) MF — Pass Accuracy
scatter_topN_metric_by_position(
    df,
    position="MF",
    x_mean_col="PassAcc%_mean",
    y_cv_col="CV_PassAcc%",
    title=f"MF (Top {TOP_N_METRIC} in Pass Accuracy): Performance vs Consistency",
    xlabel="Pass Accuracy (%) (mean)",
    ylabel="CV Pass Accuracy (%)",
    filename="12_MF_PassAcc_mean_vs_CV_PassAcc_top15.png",
    top_n=TOP_N_METRIC,
    invert_y=True
)

# 3) FW — xG
scatter_topN_metric_by_position(
    df,
    position="FW",
    x_mean_col="xG_90_mean",
    y_cv_col="CV_xG_90",
    title=f"FW (Top {TOP_N_METRIC} in xG/90): Performance vs Consistency",
    xlabel="xG per 90 min (media)",
    ylabel="CV xG per 90 min (%)",
    filename="13_FW_xG_mean_vs_CV_xG_top15.png",
    top_n=TOP_N_METRIC,
    invert_y=True
)

# Visual 14: CV_Rating vs Rating_mean + tendency
plt.figure(figsize=(9, 6))
sns.regplot(
    data=df,
    x="CV_Rating",
    y="Rating_mean",
    scatter_kws={"alpha": 0.6},
    line_kws={"linewidth": 2}
)

plt.title("Consistency (CV) vs Average Rating")
plt.xlabel("CV Rating")
plt.ylabel("Average Rating")

savefig("14_cv_vs_rating_mean.png")
plt.show()

# Visual 15: CV vs Rating_mean (Top 15)
TOP_N_HIGHLIGHT = 15

# Top 15 per Rating_mean
top_rating = df.sort_values("Rating_mean", ascending=False).head(TOP_N_HIGHLIGHT)

plt.figure(figsize=(10, 6))

sns.scatterplot(
    data=df,
    x="CV_Rating",
    y="Rating_mean",
    color="lightgray",
    alpha=0.5
)

sns.scatterplot(
    data=top_rating,
    x="CV_Rating",
    y="Rating_mean",
    color="red",
    s=100
)

sns.regplot(
    data=df,
    x="CV_Rating",
    y="Rating_mean",
    scatter=False,
    color="black"
)

for _, row in top_rating.iterrows():
    plt.annotate(
        row["Name"],
        (row["CV_Rating"], row["Rating_mean"]),
        fontsize=9,
        xytext=(5, 4),
        textcoords="offset points"
    )

plt.title("Consistency (CV) vs Average Rating \nTop 15 players per Average Rating")
plt.xlabel("CV Rating (%)")
plt.ylabel("Average Rating")

savefig("14_cv_vs_rating_top15.png")
plt.show()