# Cricket Statistics Analyzer

A Python data-analysis mini project that simulates a realistic T20 cricket dataset,
computes batting and bowling performance metrics, detects statistical outliers using
the IQR method, and produces annotated scatter-plot visualisations.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Dataset](#dataset)
5. [How It Works](#how-it-works)
   - [Data Generation](#1-data-generation)
   - [Data Loading & Cleaning](#2-data-loading--cleaning)
   - [Milestone 1 – Metric Calculation](#3-milestone-1--metric-calculation)
   - [Milestone 2 – Outlier Detection](#4-milestone-2--outlier-detection)
   - [Scatter Plot Visualisations](#5-scatter-plot-visualisations)
6. [Output Files](#output-files)
7. [Installation & Usage](#installation--usage)
8. [Libraries Used](#libraries-used)
9. [Key Formulas](#key-formulas)
10. [Sample Results](#sample-results)

---

## Project Overview

Cricket produces rich numerical data for every player in every match. This project
models a fictional T20 league of 60 players spread across 8 teams. Starting from raw
CSV data it walks through the full analytics pipeline:

```
Raw CSV  →  Clean DataFrame  →  Compute Metrics  →  Detect Outliers  →  Visualise
```

The aim is to demonstrate practical use of **NumPy**, **pandas**, **Matplotlib**, and
**Seaborn** on a sports-analytics problem that is easy to reason about.

---

## Features

| # | Feature | Details |
|---|---------|---------|
| 1 | **Reproducible dataset generation** | Seeded random data (`seed=7`) for 56 players + 4 manually injected extreme outliers |
| 2 | **Data cleaning** | Removes duplicate rows, fills missing values (median for `BallsFaced`, 0 for `RunsConceded`) |
| 3 | **Batting Strike Rate** | `(Runs / Balls Faced) × 100` — measures how quickly a batter scores |
| 4 | **Batting Average** | `Runs / (Innings − Not Outs)` — measures consistency |
| 5 | **Bowling Economy** | `Runs Conceded / Overs Bowled` — lower is better for a bowler |
| 6 | **Bowling Strike Rate** | `Balls Bowled / Wickets` — how frequently a bowler takes wickets |
| 7 | **IQR outlier detection** | Applied separately to Strike Rate (batters ≥ 50 balls) and Economy (bowlers ≥ 10 overs) |
| 8 | **Three scatter plots** | Strike Rate, Economy, and All-rounder dual-skill plots, all with outliers circled |
| 9 | **Written outputs** | Outlier report (`.txt`), enriched player CSV, and mirrored console log |

---

## Project Structure

```
cricket_statistics_analyzer/
│
├── generate_cricket_data.py   # Generates cricket_stats.csv (seeded, reproducible)
├── cricket_analysis.py        # Main analysis: cleaning, metrics, outliers, plots
├── run_all.py                 # One-click runner: executes both scripts in order
├── requirements.txt           # Python dependencies
├── cricket_stats.csv          # Auto-generated input data (64 rows × 14 columns)
│
└── outputs/                   # All generated deliverables land here
    ├── console_output.txt      # Full console log mirrored to file
    ├── players_with_metrics.csv# Original data + all computed metrics
    ├── outliers.csv            # Rows flagged as outliers (Strike Rate & Economy)
    ├── outlier_report.txt      # Human-readable outlier summary with IQR bounds
    ├── scatter_strike_rate.png # Plot 1: Balls Faced vs Strike Rate
    ├── scatter_economy.png     # Plot 2: Overs Bowled vs Economy
    └── scatter_allrounder.png  # Plot 3: All-rounders Strike Rate vs Economy
```

---

## Dataset

`cricket_stats.csv` is created by `generate_cricket_data.py` and contains **64 rows**
(56 random players + 4 injected outliers + a few dirty records for cleaning demo).

### Columns

| Column | Type | Description |
|--------|------|-------------|
| `PlayerID` | string | Unique identifier (P001 – P060) |
| `Player` | string | Full name |
| `Team` | string | One of 8 fictional IPL-style franchises |
| `Role` | string | `Batsman`, `Bowler`, or `All-rounder` |
| `Matches` | int | Total matches played (8–15) |
| `Innings` | int | Batting innings |
| `Runs` | int | Total runs scored |
| `BallsFaced` | int | Total balls faced while batting |
| `Fours` | int | Number of boundaries hit |
| `Sixes` | int | Number of sixes hit |
| `NotOuts` | int | Times not dismissed |
| `BallsBowled` | int | Total balls bowled |
| `RunsConceded` | int | Runs given away while bowling |
| `Wickets` | int | Wickets taken |

### Teams

- Mumbai Strikers · Chennai Kings · Delhi Daredevils · Bengaluru Royals
- Kolkata Tigers · Punjab Lions · Rajasthan Warriors · Hyderabad Sunrisers

### Injected Outliers

Four extreme records are deliberately added to ensure the IQR detector has clear
signals to find:

| Player | Role | Anomaly |
|--------|------|---------|
| Andre Blitz | All-rounder | Strike Rate ≈ 207 (extremely aggressive batter) |
| Chris Anchor | Batsman | Strike Rate ≈ 85 (extremely slow scorer) |
| Liam Costly | Bowler | Economy ≈ 14 (very expensive bowler) |
| Rashid Miser | Bowler | Economy ≈ 4.5 (exceptionally economical bowler) |

---

## How It Works

### 1. Data Generation

`generate_cricket_data.py` uses `numpy.random.default_rng(seed=7)` to build a
statistically realistic dataset. Each player's batting and bowling numbers are drawn
from normal distributions whose parameters depend on their role:

- **Batsmen** face more balls and have higher strike rates (~138).
- **Bowlers** bowl more overs and have better economies (~7.8 runs/over).
- **All-rounders** sit in between for both metrics.

Two dirty records (a missing `BallsFaced` and a missing `RunsConceded`) plus one
duplicate row are intentionally inserted to demonstrate the cleaning step.

---

### 2. Data Loading & Cleaning

`load_and_clean()` in `cricket_analysis.py`:

1. Reads `cricket_stats.csv` into a pandas `DataFrame`.
2. Reports the raw row count.
3. Removes **duplicate rows** based on `PlayerID` (`drop_duplicates`).
4. Reports any **missing values** found per column.
5. Fills missing `BallsFaced` with the **column median** (robust to outliers).
6. Fills missing `RunsConceded` with **0** (player bowled no balls).
7. Casts both columns to `int` for consistency.

---

### 3. Milestone 1 – Metric Calculation

`calculate_metrics()` uses **NumPy vectorised operations** (`np.where`, `np.round`)
to add new columns to the DataFrame without any Python loops:

| New Column | Formula | Notes |
|------------|---------|-------|
| `StrikeRate` | `(Runs / BallsFaced) × 100` | Set to 0 if `BallsFaced == 0` |
| `BattingAvg` | `Runs / (Innings − NotOuts)` | Falls back to `Runs` if never dismissed |
| `Overs` | `BallsBowled / 6` | Rounded to 1 decimal place |
| `Economy` | `RunsConceded / Overs` | `NaN` if no balls bowled |
| `BowlingSR` | `BallsBowled / Wickets` | `NaN` if 0 wickets |

After calculation the script prints:

- **Top 5 batting strike rates** (minimum 50 balls faced).
- **Best 5 bowling economies** (minimum 10 overs bowled).
- **Average metrics grouped by role** (`Batsman`, `Bowler`, `All-rounder`).

---

### 4. Milestone 2 – Outlier Detection

`detect_outliers()` applies the **Inter-Quartile Range (IQR) method** — a
non-parametric, robust technique that does not assume a normal distribution.

**Algorithm:**

```
Q1  = 25th percentile of the metric
Q3  = 75th percentile of the metric
IQR = Q3 − Q1
Lower fence = Q1 − 1.5 × IQR
Upper fence = Q3 + 1.5 × IQR

Any value outside [Lower fence, Upper fence] is flagged as an outlier.
```

Two separate passes are made:

| Pass | Metric | Filter |
|------|--------|--------|
| 1 | `StrikeRate` | Players with `BallsFaced ≥ 50` (meaningful batting sample) |
| 2 | `Economy` | Players with `BallsBowled ≥ 60` (i.e. ≥ 10 overs bowled) |

Outliers are labelled descriptively:

- Strike Rate outliers → `"High SR"` or `"Low SR"`
- Economy outliers → `"Expensive (High Econ)"` or `"Economical (Low Econ)"`

Results are written to both `outlier_report.txt` and `outliers.csv`.

---

### 5. Scatter Plot Visualisations

`scatter_plots()` produces three publication-ready PNG charts using Matplotlib and
Seaborn (`whitegrid` theme, 150 dpi):

#### Plot 1 — `scatter_strike_rate.png`
**Balls Faced vs Strike Rate** for all batters (≥ 50 balls).
- Points are coloured by `Role`.
- Outliers are circled in red with player-name annotations.
- Dashed horizontal lines mark the IQR upper and lower bounds.

#### Plot 2 — `scatter_economy.png`
**Overs Bowled vs Economy** for all bowlers (≥ 10 overs).
- Same outlier-highlighting style as Plot 1.
- Seaborn `Set2` palette used for role colours.

#### Plot 3 — `scatter_allrounder.png`
**Strike Rate vs Economy** exclusively for All-rounders who meet both batting and
bowling minimums.
- Each point is sized uniformly but coloured by **Wickets** (viridis colour map).
- The Y-axis is **inverted** so the top-right corner represents the most desirable
  combination (high strike rate + low economy).
- First-name labels placed next to each point.

---

## Output Files

| File | Description |
|------|-------------|
| `players_with_metrics.csv` | Full dataset enriched with `StrikeRate`, `BattingAvg`, `Overs`, `Economy`, `BowlingSR` |
| `outliers.csv` | Subset of rows flagged as outliers, with an added `Metric` column indicating which metric triggered the flag |
| `outlier_report.txt` | Human-readable report showing IQR bounds, fence values, and a formatted table of each outlier |
| `console_output.txt` | Exact mirror of everything printed to the terminal during analysis (via the `Tee` class) |
| `scatter_strike_rate.png` | Scatter plot — batting analysis |
| `scatter_economy.png` | Scatter plot — bowling analysis |
| `scatter_allrounder.png` | Scatter plot — all-rounder dual-skill view |

---

## Installation & Usage

### Prerequisites

- Python 3.9 or higher
- `pip`

### Steps

```bash
# 1. Clone or download the project
cd cricket_statistics_analyzer

# 2. (Recommended) Create and activate a virtual environment
#    Windows:
python -m venv venv
venv\Scripts\activate

#    Mac / Linux:
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4a. Run everything at once (recommended)
python run_all.py

# 4b. Or run step by step
python generate_cricket_data.py   # creates cricket_stats.csv
python cricket_analysis.py        # runs the full analysis

# 5. Inspect the outputs/ folder for CSVs, reports, and scatter plots
```

> On Mac/Linux use `python3` / `pip3` if `python` points to Python 2.

---

## Libraries Used

| Library | Version requirement | Purpose |
|---------|-------------------|---------|
| **NumPy** | ≥ 1.21 | Vectorised arithmetic, random number generation, `np.where` |
| **pandas** | ≥ 1.3 | DataFrame manipulation, groupby, CSV I/O |
| **Matplotlib** | ≥ 3.4 | Figure/axes creation, scatter plots, annotations |
| **Seaborn** | ≥ 0.11 | High-level scatter plots, whitegrid theme |

Install all at once: `pip install -r requirements.txt`

---

## Key Formulas

```
Batting Strike Rate  = (Runs Scored / Balls Faced) × 100
Batting Average      = Runs Scored / (Innings Batted − Not Outs)

Bowling Economy      = Runs Conceded / Overs Bowled
                     = Runs Conceded / (Balls Bowled / 6)
Bowling Strike Rate  = Balls Bowled / Wickets Taken

IQR                  = Q3 − Q1
Outlier Lower Fence  = Q1 − 1.5 × IQR
Outlier Upper Fence  = Q3 + 1.5 × IQR
```

---

## Sample Results

```
Players analysed     : 60
Strike Rate outliers : 2  (Andre Blitz – High SR, Chris Anchor – Low SR)
Economy outliers     : 2  (Liam Costly – Expensive, Rashid Miser – Economical)
Highest Strike Rate  : Andre Blitz  (206.x)
Best Economy         : Rashid Miser (4.5x)
```

Three scatter plots are generated in `outputs/`, each with outlier players
circled in red and annotated with their names for quick visual identification.
