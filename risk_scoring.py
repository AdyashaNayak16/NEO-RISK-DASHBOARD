import pandas as pd

INPUT_CSV = "neo_data.csv"
OUTPUT_CSV = "neo_data_scored.csv"

SIZE_WEIGHT = 0.4
VELOCITY_WEIGHT = 0.3
PROXIMITY_WEIGHT = 0.3


def normalize(series: pd.Series, invert: bool = False) -> pd.Series:
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return pd.Series(0.5, index=series.index)
    scaled = (series - min_val) / (max_val - min_val)
    return 1 - scaled if invert else scaled


def compute_risk_score(df: pd.DataFrame) -> pd.Series:
    size = pd.to_numeric(df["estimated_diameter_max_km"], errors="coerce")
    velocity = pd.to_numeric(df["velocity_kmh"], errors="coerce")
    miss_distance = pd.to_numeric(df["miss_distance_km"], errors="coerce")

    size_score = normalize(size)
    velocity_score = normalize(velocity)
    proximity_score = normalize(miss_distance, invert=True)

    score = (
        SIZE_WEIGHT * size_score
        + VELOCITY_WEIGHT * velocity_score
        + PROXIMITY_WEIGHT * proximity_score
    ) * 100
    return score.round(2)


def categorize_risk(score: float) -> str:
    if score <= 25:
        return "Low"
    if score <= 50:
        return "Moderate"
    if score <= 75:
        return "High"
    return "Critical"


def scale_comparison(diameter_km: float) -> str:
    if pd.isna(diameter_km):
        return "unknown size"

    if diameter_km < 0.01:
        return "smaller than a bus"
    if diameter_km < 0.03:
        return "about the size of a bus"
    if diameter_km < 0.11:
        return "about the size of a house"
    if diameter_km < 0.33:
        return "about the size of a football field"
    if diameter_km < 0.44:
        return "about the height of the Eiffel Tower"
    if diameter_km < 1.0:
        return "larger than the Eiffel Tower"
    return "larger than the Empire State Building"


def score_neo_data(df: pd.DataFrame) -> pd.DataFrame:
    scored = df.copy()
    scored["risk_score"] = compute_risk_score(scored)
    scored["risk_category"] = scored["risk_score"].apply(categorize_risk)
    scored["scale_comparison"] = scored["estimated_diameter_max_km"].apply(scale_comparison)
    return scored


def main() -> None:
    df = pd.read_csv(INPUT_CSV)
    scored = score_neo_data(df)
    scored.to_csv(OUTPUT_CSV, index=False)

    top_5 = scored.nlargest(5, "risk_score")[
        ["name", "risk_score", "risk_category", "scale_comparison", "close_approach_date"]
    ]
    print("Top 5 highest risk asteroids:")
    print(top_5.to_string(index=False))
    print(f"\nSaved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
