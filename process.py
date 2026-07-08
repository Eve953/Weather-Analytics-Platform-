import sqlite3
import requests as r
import pandas as pd 

cities = [
    {"name": "Phoenix", "lat": 33.4483, "lon": -112.0740, "tz": "America/Phoenix"},
    {"name": "Dallas", "lat": 32.7765, "lon": -96.7970, "tz": "America/Chicago"},
    {"name": "Tokyo", "lat": 35.6895, "lon": 139.6917, "tz": "Asia/Tokyo"}
]

url = "https://archive-api.open-meteo.com/v1/archive"
city_dfs = []

for city in cities:
    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "timezone": city["tz"]
    }
    
    response = r.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        city_df = pd.DataFrame(data['daily'])
        city_df['city_name'] = city['name']
        city_dfs.append(city_df)
    else:
        print(f"Failure to retrieve data for {city['name']}. Status code: {response.status_code}")

df_master = pd.concat(city_dfs, ignore_index=True)

df_master.dropna(inplace=True)
df_master['date'] = pd.to_datetime(df_master['time']).dt.date
df_master.drop(columns=['time'], inplace=True)
df_master.drop_duplicates(inplace=True)

conn = sqlite3.connect('weather_db.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE cities (
    city_id INTEGER PRIMARY KEY,
    city_name TEXT,
    latitude NUMERIC,
    longitude NUMERIC,
    timezone TEXT
)
''')

cursor.execute('''
CREATE TABLE weather_records (
    record_id INTEGER PRIMARY KEY,
    city_id INTEGER,
    record_date TEXT,
    temp_max NUMERIC,
    temp_min NUMERIC,
    precipitation NUMERIC,
    max_wind_speed NUMERIC,
    FOREIGN KEY (city_id) REFERENCES cities (city_id)
)
''')
conn.commit()

city_id_map = {}
for city in cities:
    cursor.execute('''
    INSERT OR IGNORE INTO cities (city_name, latitude, longitude, timezone)
    VALUES (?, ?, ?, ?)
    ''', (city['name'], city['lat'], city['lon'], city['tz']))
    
    cursor.execute('SELECT city_id FROM cities WHERE city_name = ?', (city['name'],))
    city_id_map[city['name']] = cursor.fetchone()[0]

conn.commit()

df_master['city_id'] = df_master['city_name'].map(city_id_map)

for _, row in df_master.iterrows():
    cursor.execute('''
    INSERT INTO weather_records (city_id, record_date, temp_max, temp_min, precipitation, max_wind_speed)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        int(row['city_id']),
        str(row['date']),
        float(row['temperature_2m_max']),
        float(row['temperature_2m_min']),
        float(row['precipitation_sum']),
        float(row['wind_speed_10m_max'])
    ))

conn.commit()
conn.close()