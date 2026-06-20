import requests
import pandas as pd
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("SUPABASE_HOST")
DB_DB = os.getenv("SUPABASE_DB")
DB_USER = os.getenv("SUPABASE_USER")
DB_PASSWORD = quote_plus(os.getenv("SUPABASE_PASSWORD"))
DB_PORT = os.getenv("SUPABASE_PORT")

engine = create_engine(
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DB}",
    connect_args={"sslmode": "require"}
)

STATIONS = {
    "Hathnikund Barrage": "009-UYDDEL",
    "Fatehgarh": "038-UYDDEL",
    "Kalanaur": "010-UYDDEL"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def fetch_history(station_code, days_back):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)

    start_str = start_date.strftime("%Y-%m-%dT%H:%M:%S.000")
    end_str = end_date.strftime("%Y-%m-%dT%H:%M:%S.000")

    url = f'https://ffs.india-water.gov.in/iam/api/new-entry-data/specification/sorted?sort-criteria=%7B%22sortOrderDtos%22:%5B%7B%22sortDirection%22:%22ASC%22,%22field%22:%22id.dataTime%22%7D%5D%7D&specification=%7B%22where%22:%7B%22where%22:%7B%22where%22:%7B%22expression%22:%7B%22valueIsRelationField%22:false,%22fieldName%22:%22id.stationCode%22,%22operator%22:%22eq%22,%22value%22:%22{station_code}%22%7D%7D,%22and%22:%7B%22expression%22:%7B%22valueIsRelationField%22:false,%22fieldName%22:%22id.datatypeCode%22,%22operator%22:%22eq%22,%22value%22:%22HHS%22%7D%7D%7D,%22and%22:%7B%22expression%22:%7B%22valueIsRelationField%22:false,%22fieldName%22:%22dataValue%22,%22operator%22:%22null%22,%22value%22:%22false%22%7D%7D%7D,%22and%22:%7B%22expression%22:%7B%22valueIsRelationField%22:false,%22fieldName%22:%22id.dataTime%22,%22operator%22:%22btn%22,%22value%22:%22{start_str},{end_str}%22%7D%7D%7D'

    response = requests.get(url, headers=HEADERS)
    return response.json()

if __name__ == "__main__":
    all_records = []

    for station_name, station_code in STATIONS.items():
        print(f"Fetching 90 days of history for {station_name}...")
        data = fetch_history(station_code, days_back=90)
        print(f"  -> {len(data)} records found")

        for record in data:
            all_records.append({
                "station": station_name,
                "station_code": station_code,
                "water_level": record.get("dataValue"),
                "reading_time": record.get("id", {}).get("dataTime"),
                "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    df = pd.DataFrame(all_records)
    print(f"\nTotal records collected: {len(df)}")

    # Save to CSV backup
    df.to_csv("data/river_history_backfill.csv", index=False)

    # Save to database
    df_db = df.copy()
    df_db["reading_time"] = pd.to_datetime(df_db["reading_time"])
    df_db["fetched_at"] = pd.to_datetime(df_db["fetched_at"])
    df_db.to_sql("river_levels", engine, if_exists="append", index=False)

    print("✅ Historical data backfilled to database")