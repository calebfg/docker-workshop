# Module 1 Homework — Docker & SQL
#HOMEWORK LINK - https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/cohorts/2026/01-docker-terraform/homework.md

## Question 1 — Docker pip version
**Answer: 25.3** (actual result: 26.0.1 — image updated since homework was written)

Command used:
```bash
docker run -it --rm --entrypoint=bash python:3.13
pip --version
```

## Question 2 — Docker networking
**Answer: db:5432**

Inside a Docker Compose network, containers communicate using service names 
as hostnames and container ports. pgAdmin uses `db` (the service name) and 
`5432` (the container port), not the host port `5433`.

## Question 3 — Counting short trips
**Answer: 8,007**

```sql
SELECT COUNT(*) 
FROM green_taxi_trips_table t 
WHERE 
    lpep_pickup_datetime >= '2025-11-01' AND
    lpep_pickup_datetime < '2025-12-01' AND 
    trip_distance <= 1;
```

## Question 4 — Longest trip for each day
**Answer: 2025-11-14**

```sql
SELECT 
    DATE(lpep_pickup_datetime) AS pickup_date,
    MAX(trip_distance) AS longest_trip
FROM green_taxi_trips_table t
WHERE trip_distance < 100
GROUP BY DATE(lpep_pickup_datetime)
ORDER BY longest_trip DESC
LIMIT 1;
```

## Question 5 — Biggest pickup zone
**Answer: East Harlem North**

```sql
SELECT
    z."Zone" AS "Pickup Zone",
    SUM(total_amount) AS total_revenue
FROM green_taxi_trips_table t
JOIN zones z ON t."PULocationID" = z."LocationID"
WHERE DATE(lpep_pickup_datetime) = '2025-11-18'
GROUP BY "Pickup Zone"
ORDER BY total_revenue DESC
LIMIT 1;
```

## Question 6 — Largest tip
**Answer: Yorkville West**

```sql
SELECT
    zdo."Zone" AS "Dropoff Zone",
    MAX(tip_amount) AS largest_tip
FROM green_taxi_trips_table t
JOIN zones zpu ON t."PULocationID" = zpu."LocationID"
JOIN zones zdo ON t."DOLocationID" = zdo."LocationID"
WHERE 
    zpu."Zone" = 'East Harlem North' AND 
    t.lpep_pickup_datetime >= '2025-11-01' AND
    t.lpep_pickup_datetime < '2025-12-01'
GROUP BY "Dropoff Zone"
ORDER BY largest_tip DESC
LIMIT 1;
```

## Question 7 — Terraform Workflow
**Answer: terraform init, terraform apply -auto-approve, terraform destroy**

- `terraform init` — downloads provider plugins and sets up backend
- `terraform apply -auto-approve` — generates and auto-executes the plan without confirmation prompt
- `terraform destroy` — removes all resources managed by Terraform
