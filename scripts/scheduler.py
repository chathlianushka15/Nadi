import schedule
import time
import subprocess
from datetime import datetime

def run_pipeline():
    print(f"\n🌊 Fetching river data at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    subprocess.run(["python", "scripts/fetch_river_data.py"])
    print("✅ Pipeline complete")
    print("-" * 50)

schedule.every(1).hours.do(run_pipeline)

print("🌊 Nadi pipeline started. Running every hour...")
print("-" * 50)
run_pipeline()

while True:
    schedule.run_pending()
    time.sleep(60)