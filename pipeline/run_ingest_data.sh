# run_ingest.sh
docker run -it --rm \
--network=pg-network \
taxi_ingest:v001 \
--pg-user=root \
--pg-pass=root \
--pg-host=pgdatabase \
--pg-port=5432 \
--pg-db=ny_taxi \
--target-table=yellow_taxi_trips_2021_2 \
--year=2021 \
--month=2 \
--chunksize=100000