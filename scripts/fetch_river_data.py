import requests
import pandas as pd
import os
from datetime import datetime
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

def fetch_latest_level(station_name, station_code):
    url = f'https://ffs.india-water.gov.in/iam/api/new-entry-data/specification/sorted-page?sort-criteria=%7B%22sortOrderDtos%22:%5B%7B%22sortDirection%22:%22DESC%22,%22field%22:%22id.dataTime%22%7D%5D%7D&page-number=0&page-size=1&specification=%7B%22where%22:%7B%22where%22:%7B%22expression%22:%7B%22valueIsRelationField%22:false,%22fieldName%22:%22id.stationCode%22,%22operator%22:%22eq%22,%22value%22:%22{station_code}%22%7D%7D,%22and%22:%7B%22expression%22:%7B%22valueIsRelationField%22:false,%22fieldName%22:%22id.datatypeCode%22,%22operator%22:%22eq%22,%22value%22:%22HHS%22%7D%7D%7D,%22and%22:%7B%22expression%22:%7B%22valueIsRelationField%22:false,%22fieldName%22:%22dataValue%22,%22operator%22:%22null%22,%22value%22:%22false%22%7D%7D%7D'

    response = requests.get(url, headers=HEADERS)
    data = response.json()

    if not data or len(data) == 0:
        return {
            "station": station_name,
            "station_code": station_code,
            "water_level": None,
            "reading_time": None,
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    reading = data[0]

    return {
        "station": station_name,
        "station_code": station_code,
        "water_level": reading.get("dataValue"),
        "reading_time": reading.get("id", {}).get("dataTime"),
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

if __name__ == "__main__":
    results = []
    for name, code in STATIONS.items():
        result = fetch_latest_level(name, code)
        print(result)
        results.append(result)

    df = pd.DataFrame(results)

    # Save to CSV
    df.to_csv("data/river_data.csv", index=False)

    # Save to database
    df_db = df.copy()
    df_db["reading_time"] = pd.to_datetime(df_db["reading_time"])
    df_db["fetched_at"] = pd.to_datetime(df_db["fetched_at"])
    df_db.to_sql("river_levels", engine, if_exists="append", index=False)

    print("\n✅ River data saved to CSV and database")