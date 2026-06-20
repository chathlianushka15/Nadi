import requests
from datetime import datetime, timedelta

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

station_code = "009-UYDDEL"  # Hathnikund Barrage

end_date = datetime.now()
start_date = end_date - timedelta(days=90)

start_str = start_date.strftime("%Y-%m-%dT%H:%M:%S.000")
end_str = end_date.strftime("%Y-%m-%dT%H:%M:%S.000")

url = f'https://ffs.india-water.gov.in/iam/api/new-entry-data/specification/sorted?sort-criteria=%7B%22sortOrderDtos%22:%5B%7B%22sortDirection%22:%22ASC%22,%22field%22:%22id.dataTime%22%7D%5D%7D&specification=%7B%22where%22:%7B%22where%22:%7B%22where%22:%7B%22expression%22:%7B%22valueIsRelationField%22:false,%22fieldName%22:%22id.stationCode%22,%22operator%22:%22eq%22,%22value%22:%22{station_code}%22%7D%7D,%22and%22:%7B%22expression%22:%7B%22valueIsRelationField%22:false,%22fieldName%22:%22id.datatypeCode%22,%22operator%22:%22eq%22,%22value%22:%22HHS%22%7D%7D%7D,%22and%22:%7B%22expression%22:%7B%22valueIsRelationField%22:false,%22fieldName%22:%22dataValue%22,%22operator%22:%22null%22,%22value%22:%22false%22%7D%7D%7D,%22and%22:%7B%22expression%22:%7B%22valueIsRelationField%22:false,%22fieldName%22:%22id.dataTime%22,%22operator%22:%22btn%22,%22value%22:%22{start_str},{end_str}%22%7D%7D%7D'

response = requests.get(url, headers=HEADERS)
data = response.json()

print(f"Status code: {response.status_code}")
print(f"Number of records returned: {len(data)}")
print("\nFirst 3 records:")
for record in data[:3]:
    print(record)
print("\nLast 3 records:")
for record in data[-3:]:
    print(record)