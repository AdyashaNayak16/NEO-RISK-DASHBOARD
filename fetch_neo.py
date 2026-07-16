import argparse
import os
from datetime import datetime, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv

FEED_URL = "https://api.nasa.gov/neo/rest/v1/feed"
MAX_DAYS_PER_REQUEST = 7
OUTPUT_CSV = "neo_data.csv"


def fetch_neo_feed(start_date: str, end_date: str, api_key: str) -> dict:
    response = requests.get(
        FEED_URL,
        params={
            "start_date": start_date,
            "end_date": end_date,
            "api_key": api_key,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def parse_neo_response(data: dict) -> pd.DataFrame:
    rows = []

    for date, neos in data.get("near_earth_objects", {}).items():
        for neo in neos:
            approach = next(
                (
                    entry
                    for entry in neo.get("close_approach_data", [])
                    if entry.get("close_approach_date") == date
                ),
                None,
            )
            if approach is None and neo.get("close_approach_data"):
                approach = neo["close_approach_data"][0]

            diameter_km = neo.get("estimated_diameter", {}).get("kilometers", {})
            velocity = (approach or {}).get("relative_velocity", {})
            miss_distance = (approach or {}).get("miss_distance", {})

            rows.append(
                {
                    "name": neo.get("name"),
                    "estimated_diameter_min_km": diameter_km.get("estimated_diameter_min"),
                    "estimated_diameter_max_km": diameter_km.get("estimated_diameter_max"),
                    "velocity_kmh": velocity.get("kilometers_per_hour"),
                    "miss_distance_km": miss_distance.get("kilometers"),
                    "close_approach_date": (approach or {}).get("close_approach_date", date),
                    "is_potentially_hazardous": neo.get("is_potentially_hazardous_asteroid"),
                }
            )

    return pd.DataFrame(
        rows,
        columns=[
            "name",
            "estimated_diameter_min_km",
            "estimated_diameter_max_km",
            "velocity_kmh",
            "miss_distance_km",
            "close_approach_date",
            "is_potentially_hazardous",
        ],
    )


def iter_date_chunks(start_date: str, end_date: str, max_days: int = MAX_DAYS_PER_REQUEST):
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    if start > end:
        raise ValueError("start_date must be on or before end_date")

    current = start
    while current <= end:
        chunk_end = min(current + timedelta(days=max_days - 1), end)
        yield current.isoformat(), chunk_end.isoformat()
        current = chunk_end + timedelta(days=1)


def fetch_neo_dataframe(start_date: str, end_date: str, api_key: str) -> pd.DataFrame:
    frames = []
    for chunk_start, chunk_end in iter_date_chunks(start_date, end_date):
        data = fetch_neo_feed(chunk_start, chunk_end, api_key)
        frames.append(parse_neo_response(data))

    if not frames:
        return parse_neo_response({})

    return pd.concat(frames, ignore_index=True)


def main() -> None:
    load_dotenv()
    api_key = os.getenv("NASA_API_KEY")
    if not api_key:
        raise SystemExit("NASA_API_KEY not found in .env")

    parser = argparse.ArgumentParser(description="Fetch NASA NeoWs feed data")
    parser.add_argument("start_date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("end_date", help="End date (YYYY-MM-DD)")
    args = parser.parse_args()

    df = fetch_neo_dataframe(args.start_date, args.end_date, api_key)
    df.to_csv(OUTPUT_CSV, index=False)

    total = len(df)
    hazardous = int(df["is_potentially_hazardous"].sum()) if total else 0
    print(f"Total asteroids fetched: {total}")
    print(f"Potentially hazardous: {hazardous}")
    print(f"Saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
