#!/usr/bin/env python
# coding: utf-8

# ═══════════════════════════════════════════════════════════════════
# WHAT THIS SCRIPT DOES (plain english)
# ═══════════════════════════════════════════════════════════════════
#
# This script is a data ingestion pipeline.
# It downloads the NYC Yellow Taxi trip dataset from the web
# and loads it into a PostgreSQL database table called yellow_taxi_data.
#
# STEP 1 — SETUP
# We define the data types for each column so pandas reads them
# correctly instead of guessing. We also tell pandas which columns
# are dates so they are stored as proper timestamps, not plain text.
#
# STEP 2 — DATABASE CONNECTION
# We create a connection configuration (engine) that tells SQLAlchemy
# where PostgreSQL is running and how to log in.
# No actual connection is made yet at this point.
#
# STEP 3 — SAFETY CHECK
# Before inserting anything, we check if the table already exists.
# If it does, we wipe it clean (TRUNCATE) so that running this script
# more than once does not create duplicate rows.
#
# STEP 4 — READ IN CHUNKS
# The dataset has 1.3 million rows. Instead of loading everything
# into memory at once, we read 100,000 rows at a time.
# This keeps memory usage low and makes the script scalable.
#
# STEP 5 — CREATE THE TABLE
# We use the first chunk to create the table structure in PostgreSQL.
# No data is inserted yet — just the column names and types.
#
# STEP 6 — INSERT DATA
# We insert the first chunk, then loop through all remaining chunks
# and insert them one at a time. A progress bar shows how far along
# the ingestion is.
#
# STEP 7 — DONE
# All 1.3 million rows are now in PostgreSQL and ready to be queried.
#
# ═══════════════════════════════════════════════════════════════════

import pandas as pd
from sqlalchemy import create_engine, text
from tqdm.auto import tqdm

# ── Column type definitions ───────────────────────────────────────────────────
# Defined at the top level because ingest_data() needs them
# and they never change regardless of which month we are ingesting

# Column data types — tells pandas how to read each column correctly
# Int64 (capital I) supports missing values, int64 (lowercase) does not
dataType = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

# Columns to convert from plain text to datetime objects
dateColumns = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

# ── Ingestion function ────────────────────────────────────────────────────────

def ingest_data(url, engine, target_table, chunksize=100000):

    df_iter = pd.read_csv(
        url,
        dtype=dataType,
        parse_dates=dateColumns,
        iterator=True,
        chunksize=chunksize
    )

    # Pull the first chunk out separately so we can use it to create the table
    # next() asks the iterator for its first batch of rows
    first_chunk = next(df_iter)

    # Create the table structure in PostgreSQL using the first chunk
    # head(0) means zero rows — we are only creating the columns, not inserting data yet
    # replace means: drop and recreate the table if it already exists
    first_chunk.head(0).to_sql(
        name=target_table,
        con=engine,
        if_exists="replace"
    )
    print(f"Table {target_table} created")

    # Insert the first chunk's actual data into the table
    first_chunk.to_sql(
        name=target_table,
        con=engine,
        if_exists="append"  # append adds rows without dropping the table
    )
    print(f"Inserted first chunk: {len(first_chunk)}")

    # Loop through all remaining chunks and insert them one at a time
    # tqdm wraps df_iter to show a live progress bar during the loop
    for df_chunk in tqdm(df_iter):
        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists="append"
        )
        print(f"Inserted chunk: {len(df_chunk)}")

    print(f"Done! All data inserted into {target_table}.")

# ── Main function ─────────────────────────────────────────────────────────────

import click

# @click.command() turns main() into a command line tool
# @click.option() defines each argument you can pass from the terminal
# default= is the fallback value if you don't pass that argument
# type=int means click converts the string input to an integer automatically
# help= is the description shown when you run: python ingest_data.py --help
@click.command()
@click.option('--pg-user',      default='root',             help='PostgreSQL username')
@click.option('--pg-pass',      default='root',             help='PostgreSQL password')
@click.option('--pg-host',      default='localhost',        help='PostgreSQL host')
@click.option('--pg-port',      default='5432',             help='PostgreSQL port')
@click.option('--pg-db',        default='ny_taxi',          help='PostgreSQL database name')
@click.option('--year',         default=2021,  type=int,    help='Year of the data')
@click.option('--month',        default=1,     type=int,    help='Month of the data')
@click.option('--chunksize',    default=100000,type=int,    help='Chunk size for ingestion')
@click.option('--target-table', default='yellow_taxi_data', help='Target table name')


def main(pg_user, pg_pass, pg_host, pg_port, pg_db, year, month, chunksize, target_table):
    # Build the database connection using the credentials passed from terminal
    # does NOT open a connection yet — just stores the configuration
    engine = create_engine(f'postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}')

    # Build the URL dynamically using year and month passed from terminal
    # :04d ensures year is always 4 digits (e.g. 2021)
    # :02d ensures month is always 2 digits (e.g. 01, 02 ... 12)
    url_prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow'
    url = f'{url_prefix}/yellow_tripdata_{year:04d}-{month:02d}.csv.gz'

    # Run the ingestion passing all required arguments
    ingest_data(
        url=url,
        engine=engine,
        target_table=target_table,
        chunksize=chunksize
    )

# This means: only run main() if this file is executed directly
# If this file is imported by another script, main() will NOT run automatically
if __name__ == '__main__':
    main()