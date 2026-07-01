import requests as r
import pandas as pd 

city_dfs = []

cities = [
    {"name": "Phoenix", "lat": 33.4483, "lon": -112.0740, "tz": "America/Phoenix"},
    {"name": "Dallas", "lat": 32.7765, "lon": -96.7970, "tz": "America/Chicago"},
    {"name": "Tokyo", "lat": 35.6895, "lon": 139.6917, "tz": "Asia/Tokyo"}
]

url = "https://archive-api.open-meteo.com/v1/archive"

for city in cities:
    coords = city
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "start_date": "2023-01-01",
        "end_date": "2023-12-31",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "timezone": coords["tz"]
    }
    
    response = r.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # FIX 1: This block must be inside the IF statement
        city_df = pd.DataFrame(data['daily'])
        city_df['city_name'] = city['name']
        city_dfs.append(city_df)
        print(f"Successfully retrieved data for {city['name']}")
    else:
        # This only runs if the API fails
        print(f"Failure to retrieve data for {city['name']}. The status code is: {response.status_code}")

# FIX 2: This is completely outside the loop (no indentation)
# It takes the list of ALL accumulated city dataframes and merges them into one master dataframe.
df_master = pd.concat(city_dfs, ignore_index=True)

# Test print to make sure it worked
print("\nSuccess! Here is a preview of the combined data:")
print(df_master.head())