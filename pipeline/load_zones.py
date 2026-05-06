# load_zones.py
# Downloads the NYC Taxi Zone lookup table and loads it into PostgreSQL
# The zones table maps location ID numbers to real neighbourhood names
# This is needed for JOIN queries in the SQL refresher

import pandas as pd
from sqlalchemy import create_engine

# connect to PostgreSQL — same credentials as ingest_data.py
engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')

# zones CSV is small (265 rows) — no chunking needed
url = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/misc/taxi_zone_lookup.csv'

# read the full CSV into memory
df_zones = pd.read_csv(url)

# preview what we got
print(df_zones.head())
print(f"\nShape: {df_zones.shape}")
print(f"\nColumn types:\n{df_zones.dtypes}")

# load into PostgreSQL
# replace — safe here since zones data never changes
df_zones.to_sql(name='zones', con=engine, if_exists='replace')
print(f"\nDone! Loaded {len(df_zones)} zones into PostgreSQL.")