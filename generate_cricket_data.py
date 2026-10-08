# Creates cricket_stats.csv - sample T20 batting and bowling data for the project.
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
teams = ["Mumbai Strikers", "Chennai Kings", "Delhi Daredevils", "Bengaluru Royals",
         "Kolkata Tigers", "Punjab Lions", "Rajasthan Warriors", "Hyderabad Sunrisers"]
roles = ["Batsman", "Bowler", "All-rounder"]

first = ["Rohit", "Virat", "Rishabh", "Shreyas", "Suryakumar", "Hardik", "Ravindra", "Jasprit",
         "Mohammed", "Yuzvendra", "KL", "Shubman", "Ishan", "Sanju", "Axar", "Kuldeep", "Deepak",
         "Shardul", "Bhuvneshwar", "Washington", "Ruturaj", "Tilak", "Rinku", "Arshdeep", "Mukesh",
         "Prasidh", "Avesh", "Varun", "Tushar", "Nitish", "Rahul", "Venkatesh", "Abhishek", "Dhruv",
         "Yashasvi", "Sai", "Harshal", "Umran", "Rajat", "Mayank", "Jitesh", "Nehal", "Rasikh", "Anuj",
         "Mohsin", "Simarjeet", "Akash", "Vijay", "Naveen", "Mahipal"]
last = ["Sharma", "Kohli", "Pant", "Iyer", "Yadav", "Pandya", "Jadeja", "Bumrah", "Siraj", "Chahal",
        "Rahul", "Gill", "Kishan", "Samson", "Patel", "Singh", "Chahar", "Thakur", "Kumar", "Sundar"]

n = 56
rows = []
used = set()
for i in range(n):
    while True:
        name = f"{rng.choice(first)} {rng.choice(last)}"
        if name not in used:
            used.add(name)
            break
    role = rng.choice(roles, p=[0.42, 0.33, 0.25])
    team = teams[i % len(teams)]
    matches = int(rng.integers(8, 16))
    innings = max(1, matches - int(rng.integers(0, 3)))

    # ---- Batting ----
    if role == "Batsman":
        balls = int(rng.integers(220, 460))
        sr = rng.normal(138, 12)
    elif role == "All-rounder":
        balls = int(rng.integers(140, 320))
        sr = rng.normal(132, 14)
    else:  # Bowler - tail-ender batting
        balls = int(rng.integers(20, 90))
        sr = rng.normal(118, 18)
    runs = int(max(0, balls * sr / 100 + rng.normal(0, 8)))
    not_outs = int(rng.integers(0, 4))
    fours = int(runs * rng.uniform(0.07, 0.11))
    sixes = int(runs * rng.uniform(0.02, 0.05))

    # ---- Bowling ----
    if role == "Bowler":
        overs_whole = int(rng.integers(28, 52))
        econ = rng.normal(7.8, 0.9)
        wickets = int(rng.integers(8, 22))
    elif role == "All-rounder":
        overs_whole = int(rng.integers(14, 34))
        econ = rng.normal(8.3, 1.0)
        wickets = int(rng.integers(4, 14))
    else:  # pure batsman - minimal/none bowling
        overs_whole = int(rng.integers(0, 6))
        econ = rng.normal(9.0, 1.2)
        wickets = int(rng.integers(0, 3))
    balls_bowled = overs_whole * 6 + int(rng.integers(0, 6))
    runs_conceded = int(max(0, (balls_bowled / 6) * econ + rng.normal(0, 4)))

    rows.append([f"P{i+1:03d}", name, team, role, matches, innings, runs, balls, fours, sixes,
                 not_outs, balls_bowled, runs_conceded, wickets])

df = pd.DataFrame(rows, columns=["PlayerID", "Player", "Team", "Role", "Matches", "Innings", "Runs",
                                 "BallsFaced", "Fours", "Sixes", "NotOuts", "BallsBowled",
                                 "RunsConceded", "Wickets"])

# ---- Inject clear outliers (for Milestone 2) ----
# extreme strike rate ~207
df.loc[len(df)] = ["P057", "Andre Blitz", "Kolkata Tigers", "All-rounder",
                   12, 11, 410, 198, 28, 26, 5, 210, 360, 9]
# very low strike rate ~85
df.loc[len(df)] = ["P058", "Chris Anchor", "Punjab Lions", "Batsman",
                   11, 11, 198, 232, 14, 2, 1, 0, 0, 0]
# very expensive economy ~14
df.loc[len(df)] = ["P059", "Liam Costly", "Delhi Daredevils", "Bowler",
                   10, 4, 22, 20, 1, 1, 2, 240, 560, 7]
# very economical ~4.5
df.loc[len(df)] = ["P060", "Rashid Miser", "Hyderabad Sunrisers", "Bowler",
                   14, 5, 48, 40, 3, 2, 3, 336, 252, 24]

# a couple of dirty records to demonstrate cleaning
df.loc[3, "BallsFaced"] = np.nan
df.loc[21, "RunsConceded"] = np.nan
df = pd.concat([df, df.iloc[[10]]], ignore_index=True)  # duplicate row

df.to_csv("cricket_stats.csv", index=False)
print(f"cricket_stats.csv created with {len(df)} rows, {df.shape[1]} columns")
