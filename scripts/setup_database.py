import os
from sqlalchemy import create_engine, text
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

def setup():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS river_levels (
                id SERIAL PRIMARY KEY,
                station VARCHAR(100),
                station_code VARCHAR(50),
                water_level FLOAT,
                reading_time TIMESTAMP,
                fetched_at TIMESTAMP
            )
        """))
        conn.commit()
        print("✅ river_levels table created successfully")

if __name__ == "__main__":
    setup()