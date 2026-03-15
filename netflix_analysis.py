"""
Netflix Movies & TV Shows Analysis
====================================
Covers:
  1. Data loading & cleaning
  2. Exploratory analysis (content type, genres, countries, yearly trends)
  3. Visualizations saved as PNG files
  4. Summary of key findings printed to console
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings("ignore")

# ── 0. CONFIG ────────────────────────────────────────────────────────────────
FILE_PATH = "netflix_titles.csv"
OUTPUT_DIR = "."

NETFLIX_RED = "#E50914"
DARK        = "#221F1F"
GRAY        = "#888780"
COLORS      = ["#E50914", "#B20710", "#F5A623", "#4C72B0", "#55A868",
               "#8172B2", "#64B5CD", "#C44E52", "#CCB974", "#1D9E75"]

plt.rcParams.update({
    "figure.dpi": 150,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 11,
})

# ── 1. LOAD & CLEAN ──────────────────────────────────────────────────────────
print("=" * 60)
print("NETFLIX CATALOG ANALYSIS")
print("=" * 60)

df = pd.read_csv(FILE_PATH)
print(f"\n[1] Raw dataset shape: {df.shape}")

# Drop duplicates
dupes = df.duplicated().sum()
df.drop_duplicates(inplace=True)
print(f"    Duplicate rows removed : {dupes}")

# Missing values
missing = df.isnull().sum()
missing = missing[missing > 0]
print(f"    Columns with missing values:\n{missing.to_string()}")

# Parse date_added
df["date_added"] = pd.to_datetime(df["date_added"].str.strip(), format="%B %d, %Y", errors="coerce")
df["year_added"] = df["date_added"].dt.year
df["month_added"] = df["date_added"].dt.month

print(f"\n    Total titles   : {len(df):,}")
print(f"    Movies         : {(df['type']=='Movie').sum():,}")
print(f"    TV Shows       : {(df['type']=='TV Show').sum():,}")
print(f"    Date range     : {df['year_added'].min():.0f} – {df['year_added'].max():.0f}")

# ── 2. EXPLORATORY ANALYSIS ──────────────────────────────────────────────────
print("\n[2] Exploratory Analysis")

# 2a. Content type breakdown
type_counts = df["type"].value_counts()
print(f"\n  Content type breakdown:\n{type_counts.to_string()}")

# 2b. Top genres (listed_in has comma-separated genres)
genres = (
    df["listed_in"]
    .dropna()
    .str.split(", ")
    .explode()
    .str.strip()
    .value_counts()
    .head(10)
)
print(f"\n  Top 10 genres:\n{genres.to_string()}")

# 2c. Top countries
countries = (
    df["country"]
    .dropna()
    .str.split(", ")
    .explode()
    .str.strip()
    .value_counts()
    .head(10)
)
print(f"\n  Top 10 countries:\n{countries.to_string()}")

# 2d. Titles added per year
yearly = (
    df[df["year_added"] >= 2010]
    .groupby(["year_added", "type"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

# 2e. Top ratings
ratings = df["rating"].value_counts().head(8)

# ── 3. VISUALISATIONS ────────────────────────────────────────────────────────
print("\n[3] Creating charts …")

def save(fig, name):
    path = f"{OUTPUT_DIR}/{name}"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"    Saved → {path}")


# Chart 1 – Movies vs TV Shows (donut)
fig, ax = plt.subplots(figsize=(6, 6))
wedges, texts, autotexts = ax.pie(
    type_counts,
    labels=type_counts.index,
    autopct="%1.1f%%",
    colors=[NETFLIX_RED, DARK],
    startangle=90,
    wedgeprops=dict(width=0.5),
    textprops={"fontsize": 13}
)
for at in autotexts:
    at.set_color("white")
    at.set_fontweight("bold")
ax.set_title("Movies vs TV Shows", fontweight="bold", pad=16, fontsize=14)
save(fig, "chart1_content_type.png")


# Chart 2 – Top 10 Genres
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.barh(genres.index[::-1], genres.values[::-1], color=NETFLIX_RED)
ax.bar_label(bars, padding=4, fontsize=10)
ax.set_xlabel("Number of Titles")
ax.set_title("Top 10 Genres on Netflix", fontweight="bold", pad=12)
ax.set_xlim(0, genres.max() * 1.18)
save(fig, "chart2_top_genres.png")


# Chart 3 – Top 10 Countries
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.barh(countries.index[::-1], countries.values[::-1], color=COLORS[:10])
ax.bar_label(bars, padding=4, fontsize=10)
ax.set_xlabel("Number of Titles")
ax.set_title("Top 10 Countries by Netflix Content", fontweight="bold", pad=12)
ax.set_xlim(0, countries.max() * 1.18)
save(fig, "chart3_top_countries.png")


# Chart 4 – Titles Added Per Year (stacked bar)
fig, ax = plt.subplots(figsize=(11, 5))
years = yearly["year_added"].astype(int)
if "Movie" in yearly.columns:
    ax.bar(years, yearly["Movie"], label="Movie", color=NETFLIX_RED)
if "TV Show" in yearly.columns:
    bottom = yearly["Movie"] if "Movie" in yearly.columns else 0
    ax.bar(years, yearly["TV Show"], bottom=bottom, label="TV Show", color=DARK)
ax.set_xlabel("Year")
ax.set_ylabel("Titles Added")
ax.set_title("Titles Added to Netflix Per Year", fontweight="bold", pad=12)
ax.legend()
ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
save(fig, "chart4_titles_per_year.png")


# Chart 5 – Content Ratings Distribution
fig, ax = plt.subplots(figsize=(9, 4))
bars = ax.bar(ratings.index, ratings.values, color=COLORS[:len(ratings)], edgecolor="none")
ax.bar_label(bars, padding=3, fontsize=10)
ax.set_ylabel("Number of Titles")
ax.set_title("Content Rating Distribution", fontweight="bold", pad=12)
ax.set_ylim(0, ratings.max() * 1.18)
save(fig, "chart5_content_ratings.png")


# ── 4. KEY FINDINGS ──────────────────────────────────────────────────────────
movie_pct   = type_counts.get("Movie", 0) / len(df) * 100
top_genre   = genres.idxmax()
top_country = countries.idxmax()
peak_year   = int(yearly.loc[(yearly.get("Movie", 0) + yearly.get("TV Show", 0)).idxmax() if "Movie" in yearly.columns else yearly["TV Show"].idxmax(), "year_added"])
top_rating  = ratings.idxmax()

print("\n" + "=" * 60)
print("KEY FINDINGS")
print("=" * 60)
print(f"  • Movies make up       : {movie_pct:.1f}% of the catalog")
print(f"  • Most common genre    : {top_genre}")
print(f"  • Top producing country: {top_country} ({countries.max():,} titles)")
print(f"  • Peak content year    : {peak_year}")
print(f"  • Most common rating   : {top_rating} ({ratings.max():,} titles)")
print("\nAll charts saved as PNG files.")
print("=" * 60)
