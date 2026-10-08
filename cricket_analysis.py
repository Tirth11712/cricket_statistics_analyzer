"""
Cricket Statistics Analyzer - Mini Project
Calculates batting Strike Rate and bowling Economy, detects outliers using the
IQR method, and draws scatter plots.
Libraries: numpy, pandas, matplotlib, seaborn
"""
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

DATA_FILE = "cricket_stats.csv"
OUT_DIR = "outputs"
os.makedirs(OUT_DIR, exist_ok=True)
sns.set_theme(style="whitegrid", font_scale=0.95)
pd.set_option("display.width", 130)
pd.set_option("display.float_format", lambda v: f"{v:,.2f}")


class Tee:
    """Send everything printed to both the screen and outputs/console_output.txt."""
    def __init__(self, *streams):
        self.streams = streams

    def write(self, data):
        for s in self.streams:
            s.write(data)

    def flush(self):
        for s in self.streams:
            s.flush()


def banner(t):
    print("\n" + "=" * 72 + f"\n {t}\n" + "=" * 72)


# DATA LOADING & CLEANING
def load_and_clean(path):
    banner("DATA LOADING & CLEANING")
    df = pd.read_csv(path)
    print(f"Raw records loaded     : {len(df)}")
    dupes = df.duplicated(subset="PlayerID").sum()
    df = df.drop_duplicates(subset="PlayerID")
    print(f"Duplicate rows removed : {dupes}")
    print(f"Missing values         : {df.isna().sum()[df.isna().sum() > 0].to_dict()}")
    # fill missing numeric fields sensibly
    df["BallsFaced"] = df["BallsFaced"].fillna(df["BallsFaced"].median())
    df["RunsConceded"] = df["RunsConceded"].fillna(0)
    df = df.astype({"BallsFaced": int, "RunsConceded": int})
    print(f"Clean records          : {len(df)} | Teams: {df['Team'].nunique()} "
          f"| Roles: {df['Role'].nunique()}")
    return df.reset_index(drop=True)


# MILESTONE 1 : METRIC CALCULATION
def calculate_metrics(df):
    banner("MILESTONE 1 : METRIC CALCULATION (Strike Rate & Economy)")

    # --- Batting Strike Rate = (Runs / Balls Faced) * 100 ---
    df["StrikeRate"] = np.where(df["BallsFaced"] > 0,
                                np.round(df["Runs"] / df["BallsFaced"] * 100, 2), 0.0)
    # Batting average (for context)
    outs = (df["Innings"] - df["NotOuts"]).replace(0, np.nan)
    df["BattingAvg"] = np.round(df["Runs"] / outs, 2).fillna(df["Runs"])

    # --- Bowling Economy = Runs Conceded / Overs ; Overs = Balls Bowled / 6 ---
    df["Overs"] = np.round(df["BallsBowled"] / 6, 1)
    df["Economy"] = np.where(df["BallsBowled"] > 0,
                             np.round(df["RunsConceded"] / (df["BallsBowled"] / 6), 2), np.nan)
    df["BowlingSR"] = np.where(df["Wickets"] > 0,
                               np.round(df["BallsBowled"] / df["Wickets"], 2), np.nan)

    print("Formulas used:")
    print("  Strike Rate    = (Runs / Balls Faced) * 100")
    print("  Bowling Economy= Runs Conceded / (Balls Bowled / 6)")
    print("  Bowling S.Rate = Balls Bowled / Wickets\n")

    batters = df[df["BallsFaced"] >= 50].sort_values("StrikeRate", ascending=False)
    print("Top 5 Strike Rates (min 50 balls faced):")
    cols = ["Player", "Team", "Role", "Runs", "BallsFaced", "StrikeRate"]
    print(batters[cols].head().to_string(index=False))

    bowlers = df[df["BallsBowled"] >= 60].sort_values("Economy")
    print("\nBest 5 Bowling Economies (min 10 overs):")
    cols = ["Player", "Team", "Role", "Overs", "RunsConceded", "Wickets", "Economy"]
    print(bowlers[cols].head().to_string(index=False))

    print("\nAverage metrics by role:")
    summ = df.groupby("Role").agg(Players=("PlayerID", "count"),
                                  AvgStrikeRate=("StrikeRate", "mean"),
                                  AvgEconomy=("Economy", "mean")).round(2)
    print(summ.to_string())
    return df


# MILESTONE 2 : OUTLIER DETECTION
def iqr_bounds(s):
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr, q1, q3, iqr


def detect_outliers(df):
    banner("MILESTONE 2 : OUTLIER DETECTION (IQR method)")

    # --- Strike Rate outliers (batters with a meaningful sample) ---
    bat = df[df["BallsFaced"] >= 50].copy()
    lo, hi, q1, q3, iqr = iqr_bounds(bat["StrikeRate"])
    bat["SR_Outlier"] = (bat["StrikeRate"] < lo) | (bat["StrikeRate"] > hi)
    sr_out = bat[bat["SR_Outlier"]].copy()
    sr_out["Type"] = np.where(sr_out["StrikeRate"] > hi, "High SR", "Low SR")
    print(f"Strike Rate -> Q1={q1:.1f} Q3={q3:.1f} IQR={iqr:.1f} "
          f"bounds=[{lo:.1f}, {hi:.1f}] outliers={len(sr_out)}")
    if len(sr_out):
        print(sr_out[["Player", "Team", "Role", "BallsFaced", "StrikeRate", "Type"]]
              .sort_values("StrikeRate", ascending=False).to_string(index=False))

    # --- Economy outliers (bowlers with a meaningful sample) ---
    bowl = df[df["BallsBowled"] >= 60].copy()
    lo2, hi2, q1b, q3b, iqrb = iqr_bounds(bowl["Economy"])
    bowl["Econ_Outlier"] = (bowl["Economy"] < lo2) | (bowl["Economy"] > hi2)
    ec_out = bowl[bowl["Econ_Outlier"]].copy()
    ec_out["Type"] = np.where(ec_out["Economy"] > hi2,
                              "Expensive (High Econ)", "Economical (Low Econ)")
    print(f"\nEconomy -> Q1={q1b:.2f} Q3={q3b:.2f} IQR={iqrb:.2f} "
          f"bounds=[{lo2:.2f}, {hi2:.2f}] outliers={len(ec_out)}")
    if len(ec_out):
        print(ec_out[["Player", "Team", "Role", "Overs", "Economy", "Wickets", "Type"]]
              .sort_values("Economy", ascending=False).to_string(index=False))

    # --- Write the Outlier Report (deliverable) ---
    with open(f"{OUT_DIR}/outlier_report.txt", "w") as f:
        f.write("CRICKET STATISTICS ANALYZER - OUTLIER REPORT\n")
        f.write("=" * 60 + "\n")
        f.write("Method: Inter-Quartile Range (IQR). A value is an outlier if it\n")
        f.write("lies below Q1 - 1.5*IQR or above Q3 + 1.5*IQR.\n\n")
        f.write(f"[STRIKE RATE] bounds = [{lo:.1f}, {hi:.1f}] "
                f"(Q1={q1:.1f}, Q3={q3:.1f}, IQR={iqr:.1f})\n")
        f.write(f"Outliers found: {len(sr_out)}\n")
        f.write(sr_out[["Player", "Team", "Role", "BallsFaced", "StrikeRate", "Type"]]
                .sort_values("StrikeRate", ascending=False).to_string(index=False) + "\n\n")
        f.write(f"[ECONOMY] bounds = [{lo2:.2f}, {hi2:.2f}] "
                f"(Q1={q1b:.2f}, Q3={q3b:.2f}, IQR={iqrb:.2f})\n")
        f.write(f"Outliers found: {len(ec_out)}\n")
        f.write(ec_out[["Player", "Team", "Role", "Overs", "Economy", "Wickets", "Type"]]
                .sort_values("Economy", ascending=False).to_string(index=False) + "\n")
    print(f"\nOutlier report saved -> {OUT_DIR}/outlier_report.txt")

    pd.concat([sr_out.assign(Metric="StrikeRate"),
               ec_out.assign(Metric="Economy")]).to_csv(f"{OUT_DIR}/outliers.csv", index=False)
    return bat, bowl, (lo, hi), (lo2, hi2), sr_out, ec_out


# SCATTER PLOTS (deliverable)
def scatter_plots(df, bat, bowl, sr_bounds, ec_bounds):
    banner("SCATTER PLOTS")
    lo, hi = sr_bounds
    lo2, hi2 = ec_bounds

    # Plot 1: Balls Faced vs Strike Rate (batters) with outliers highlighted
    fig, ax = plt.subplots(figsize=(9, 5.5))
    normal = bat[~bat["SR_Outlier"]]
    out = bat[bat["SR_Outlier"]]
    sns.scatterplot(data=normal, x="BallsFaced", y="StrikeRate", hue="Role", s=70, ax=ax)
    ax.scatter(out["BallsFaced"], out["StrikeRate"], s=160, facecolors="none",
               edgecolors="red", linewidths=2, label="Outlier", zorder=5)
    for _, r in out.iterrows():
        ax.annotate(r["Player"], (r["BallsFaced"], r["StrikeRate"]),
                    textcoords="offset points", xytext=(6, 6), fontsize=8, color="darkred")
    ax.axhline(hi, ls="--", color="red", lw=1, label=f"Upper bound {hi:.0f}")
    ax.axhline(lo, ls="--", color="orange", lw=1, label=f"Lower bound {lo:.0f}")
    ax.set_title("Batting: Balls Faced vs Strike Rate (outliers circled)", fontweight="bold")
    ax.set_xlabel("Balls Faced")
    ax.set_ylabel("Strike Rate")
    ax.legend(fontsize=8, loc="lower right")
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/scatter_strike_rate.png", dpi=150)
    plt.close(fig)

    # Plot 2: Overs vs Economy (bowlers) with outliers highlighted
    fig, ax = plt.subplots(figsize=(9, 5.5))
    normalb = bowl[~bowl["Econ_Outlier"]]
    outb = bowl[bowl["Econ_Outlier"]]
    sns.scatterplot(data=normalb, x="Overs", y="Economy", hue="Role", s=70, ax=ax,
                    palette="Set2")
    ax.scatter(outb["Overs"], outb["Economy"], s=160, facecolors="none",
               edgecolors="red", linewidths=2, label="Outlier", zorder=5)
    for _, r in outb.iterrows():
        ax.annotate(r["Player"], (r["Overs"], r["Economy"]),
                    textcoords="offset points", xytext=(6, 6), fontsize=8, color="darkred")
    ax.axhline(hi2, ls="--", color="red", lw=1, label=f"Upper bound {hi2:.1f}")
    ax.axhline(lo2, ls="--", color="orange", lw=1, label=f"Lower bound {lo2:.1f}")
    ax.set_title("Bowling: Overs Bowled vs Economy (outliers circled)", fontweight="bold")
    ax.set_xlabel("Overs Bowled")
    ax.set_ylabel("Economy (runs/over)")
    ax.legend(fontsize=8, loc="upper right")
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/scatter_economy.png", dpi=150)
    plt.close(fig)

    # Plot 3: Strike Rate vs Economy for all-rounders (dual-skill view)
    ar = df[(df["Role"] == "All-rounder") & (df["BallsFaced"] >= 40) & (df["BallsBowled"] >= 60)]
    fig, ax = plt.subplots(figsize=(9, 5.5))
    sc = ax.scatter(ar["StrikeRate"], ar["Economy"], c=ar["Wickets"],
                    cmap="viridis", s=110, edgecolor="k")
    for _, r in ar.iterrows():
        ax.annotate(r["Player"].split()[0], (r["StrikeRate"], r["Economy"]),
                    textcoords="offset points", xytext=(5, 4), fontsize=7)
    ax.set_title("All-rounders: Strike Rate vs Economy (colour = wickets)", fontweight="bold")
    ax.set_xlabel("Batting Strike Rate")
    ax.set_ylabel("Bowling Economy")
    ax.invert_yaxis()  # lower economy is better -> top is better
    fig.colorbar(sc, label="Wickets")
    fig.tight_layout()
    fig.savefig(f"{OUT_DIR}/scatter_allrounder.png", dpi=150)
    plt.close(fig)

    for f in ["scatter_strike_rate.png", "scatter_economy.png", "scatter_allrounder.png"]:
        print(f"Scatter plot saved -> {OUT_DIR}/{f}")


def main():
    if not os.path.exists(DATA_FILE):
        sys.exit(f"'{DATA_FILE}' not found. Run:  python generate_cricket_data.py  first.")

    data = load_and_clean(DATA_FILE)
    data = calculate_metrics(data)
    bat, bowl, srb, ecb, sr_out, ec_out = detect_outliers(data)
    scatter_plots(data, bat, bowl, srb, ecb)
    data.to_csv(f"{OUT_DIR}/players_with_metrics.csv", index=False)
    banner("SUMMARY")
    print(f"Players analysed     : {len(data)}")
    print(f"Strike Rate outliers : {len(sr_out)} | Economy outliers: {len(ec_out)}")
    print(f"Highest Strike Rate  : {data.loc[data['StrikeRate'].idxmax(), 'Player']} "
          f"({data['StrikeRate'].max():.1f})")
    best_econ = data[data['BallsBowled'] >= 60]
    print(f"Best Economy         : {best_econ.loc[best_econ['Economy'].idxmin(), 'Player']} "
          f"({best_econ['Economy'].min():.2f})")
    print("Outputs: players_with_metrics.csv, outliers.csv, outlier_report.txt, 3 scatter plots")
    print("\nAnalysis complete.")


if __name__ == "__main__":
    # Mirror console output into outputs/console_output.txt
    log = open(f"{OUT_DIR}/console_output.txt", "w")
    original_stdout = sys.stdout
    sys.stdout = Tee(original_stdout, log)
    try:
        main()
    finally:
        sys.stdout = original_stdout
        log.close()
