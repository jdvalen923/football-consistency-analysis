import pandas as pd
import numpy as np

# Load
file_path = r"C:\Users\Valentín\OneDrive\Documentos\IE\TFGs\TFG Data\data\DATABASE_TFG_FINAL_PROCESSED.xlsx"
df_metricas = pd.read_excel(file_path, sheet_name="Sheet1")
df_minutos = pd.read_excel(file_path, sheet_name="Sheet3")

# 1) Total minutes per player + main team
total_minutos = df_minutos.groupby("Name", as_index=False)["Minutes played"].sum()

# Main team:
# - if df_minutos has column Team, we use the team with the most minutes¡
if "Team" in df_minutos.columns:
    team_primary = (
        df_minutos.groupby(["Name", "Team"], as_index=False)["Minutes played"].sum()
        .sort_values(["Name", "Minutes played"], ascending=[True, False])
        .drop_duplicates("Name")[["Name", "Team"]]
        .rename(columns={"Team": "Team"})
    )
else:
    team_primary = (
        df_metricas.groupby(["Name", "Team"], as_index=False)
        .size()
        .sort_values(["Name", "size"], ascending=[True, False])
        .drop_duplicates("Name")[["Name", "Team"]]
        .rename(columns={"Team": "Team"})
    )

# Main position
pos_primary = (
    df_metricas.groupby(["Name", "Position"], as_index=False)
    .size()
    .sort_values(["Name", "size"], ascending=[True, False])
    .drop_duplicates("Name")[["Name", "Position"]]
)

# Age
age_primary = (
    df_metricas.dropna(subset=["Age"])
    .groupby("Name", as_index=False)["Age"]
    .first()
)

# 2) Normalise metrics
metricas = ["Rating", "T+I_90", "Clearances_90", "PassAcc%", "KeyPass_90", "SoT_90", "xG_90"]

for m in metricas:
    if m == "PassAcc%" and df_metricas[m].dtype == object:
        df_metricas[m] = df_metricas[m].str.replace("%", "", regex=False).astype(float)
    df_metricas[m] = pd.to_numeric(df_metricas[m], errors="coerce")

# 3) General stats
stats = (
    df_metricas.groupby("Name")
    .agg({m: ["mean", "std"] for m in metricas})
    .reset_index()
)

stats.columns = [
    f"{c[0]}_{c[1]}" if c[1] in ["mean", "std"] else c[0]
    for c in stats.columns
]

# CVs
for m in metricas:
    stats[f"CV_{m}"] = (stats[f"{m}_std"] / stats[f"{m}_mean"]) * 100

# 4) Rating based on difficulty (mean, std, n, CV)
for lv, label in [([1, 2], "Difficult"), ([3], "Medium"), ([4, 5], "Easy")]:
    temp = (
        df_metricas[df_metricas["OppLv"].isin(lv)]
        .groupby("Name")["Rating"]
        .agg(["mean", "std", "count"])
        .reset_index()
        .rename(
            columns={
                "mean": f"Rating_{label}",
                "std": f"Rating_{label}_std",
                "count": f"Rating_{label}_n",
            }
        )
    )

    stats = pd.merge(stats, temp, on="Name", how="left")
    stats[f"CV_Rating_{label}"] = (stats[f"Rating_{label}_std"] / stats[f"Rating_{label}"]) * 100

# Gap 
stats["Gap_Easy_vs_Difficult"] = stats["Rating_Easy"] - stats["Rating_Difficult"]

# 5) Add metadata
stats = stats.merge(age_primary, on="Name", how="left")
stats = stats.merge(pos_primary, on="Name", how="left")
stats = stats.merge(team_primary, on="Name", how="left")
stats = stats.merge(total_minutos, on="Name", how="left")

# 6) Safe
stats.to_excel("DATABASE_1.xlsx", index=False)
print("✅")