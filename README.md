# Data 4: Treasure Hunt Data Warehouse

Data Engineering coursework built with PySpark, Spark SQL, Delta Lake, Kafka, PostgreSQL, MongoDB and Power BI.
The main project is a data warehouse for the "Catchem" Treasure Hunt application, with SCD Type 2 dimensions and incremental fact loading.

## Project structure

| Folder | Course part | Contents |
|---|---|---|
| [`01-course-labs/`](01-course-labs) | Labs 0–6 | Spark basics, Spark SQL, Delta tables, JDBC, a sales data warehouse and a Kafka streaming example |
| [`02-treasure-hunt-dwh/`](02-treasure-hunt-dwh) | Task 4 | Treasure Hunt data warehouse: dimensions, fact table and incremental loads |
| [`03-power-bi-report/`](03-power-bi-report) | Task 5 | Power BI report (`.pbix`) and the PDF hand-in |
| [`04-mongodb-nosql/`](04-mongodb-nosql) | Task 6 | MongoDB export, sharding and replication setup |
| [`catchem-database/`](catchem-database) | | How to restore the Catchem source database locally or on Google Cloud |
| [`docker/`](docker) | | Docker setup for Jupyter with Spark and Delta Lake, plus PostgreSQL |

Each numbered folder is self-contained. Its notebooks import the `ConnectionConfig.py` and read the `config.ini` in the same folder, and they use paths relative to that folder.

## Treasure Hunt data warehouse (Task 4)

Run the notebooks in `02-treasure-hunt-dwh/` in this order:

| Notebook | What it does |
|---|---|
| `01_DIM_DATE` | Builds the date dimension |
| `02_DIM_HOUR` | Builds the hour dimension |
| `03_DIM_SEASON` | Builds the season dimension from dates |
| `04_DIM_WEATHER` | Builds the weather dimension |
| `05_DIM_USER` | Initial load of the user dimension |
| `06_DIM_TREASURE` | Builds the treasure dimension |
| `07_FACT_TREASURE_HUNT` | Initial load of the Treasure Hunt fact table |
| `08_DIM_USER_INCREMENTAL` | Incremental user load with SCD Type 2 (Spark SQL) |
| `09_DIM_USER_INCREMENTAL_DF` | Same SCD Type 2 load, written with the DataFrame API |
| `10_FACT_TREASURE_HUNT_INCREMENTAL` | Incremental load of the fact table |
| `11_FACT_TREASURE_HUNT_INCREMENTAL_ALT` | Alternative version of the incremental fact load |
| `12_ALL_DATA` | Reads all dimensions and the fact table together for checks |

The `sql/` folder has test scripts that add or change source rows, so you can check the incremental loads:
- `test_insert_treasure.sql` and `test_insert_treasure_log.sql`: insert new source records.
- `test_update_user_dim.sql`: changes a user's city to trigger an SCD Type 2 update.

## Setup

### 1. Install and start the environment
Follow [INSTALL.md](INSTALL.md) for Python, PyCharm and the Docker containers.
`docker/docker-compose.yml` mounts this whole project into the Jupyter container at `/home/jovyan/work`.

### 2. Configuration
Connection settings live in `config.ini` files. They're git-ignored, so passwords stay on your machine.
Copy each example file and fill in your own values:

```bash
cp 01-course-labs/config.example.ini 01-course-labs/config.ini
cp 02-treasure-hunt-dwh/config.example.ini 02-treasure-hunt-dwh/config.ini
cp 04-mongodb-nosql/config.example.ini 04-mongodb-nosql/config.ini
```

### 3. Catchem database backup
The source database dump (`catchem_backup.sql`, 805 MB) is too large for the repository.
Download `catchem_backup.sql.gz` (345 MB) from the
[v1.0 release](https://github.com/nina-taghavi/data4-treasure-hunt-data-warehouse/releases/tag/v1.0),
put it in `catchem-database/`, unzip it, and restore it by following
[catchem-database/transfer_sql_to_docker.md](catchem-database/transfer_sql_to_docker.md).

```bash
gunzip catchem-database/catchem_backup.sql.gz
```
