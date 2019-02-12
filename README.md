# DataGathering

Contains all code for gathering data from exchanges such as Binance or Bitfinex.


## Using the Datapump
1. Make sure a docker container of the database is running. This can be checked by using:
    ```bash
    docker ps
    ```

    Example output:
    ```text
    13f0646a4f36 || postgres || "docker-entrypoint.s…" || 23 hours ago || Up About an hour || 0.0.0.0:5432->5432/tcp || runner_db_1
    ```
    
    If the database container is **not** running, run `docker-compose up --build` in the `Runner` project.

1. Copy `.env.example` to `.env` and adjust the parameters (DATABASE_URL and INTERVAL).
    ```bash
    cp .env.example .env
    ```

    Example (and default) `.env` file:
    ```text
    DATABASE_URL=postgresql://postgres:password@db/spreadshare
    INTERVAL=300000
    ```
    
    The `DATABASE_URL` parameter is the same url as in `runner/.env`. The `INTERVAL` parameter signifies the timespan of
    a candle.

1. Copy `CSV`files data to `input-data`. This may require `sudo` as docker may claim ownership of the folder.

    ```bash
    sudo cp *.csv ./input-data
    ```

    Data may be retrieved at: https://stack.raoulschipper.com/s/SJbO9HKFVRoWJ3J

1. Run the Datapump using:
    ```
    docker-compose up --build
    ```

## Problem and error resolution
#### Docker can't find the network `runner_default`
1. Run `docker network ls`
1. Find the network that the runner uses
1. Adjust the network in `docker-compose.yml` in two places:
    ```text
   networks:
    - runner_default
    ```
    
    ```text
    networks:
      runner_default:
        external: true
    ```

#### XXXCandles: ForeignKeyConstraint; skipping job
Some of the data is already present in the data. It is assumed that all of the data is already in the database and no
further attempt to push the data is made.

#### XXXCandles: Expected header: Timestamp, Open, Close, High, Low, Volume
A header for the csv files was expected, but not found. This is a warning and the first row, normally a header, is
actually inserted. **However, it may indicate that the order of columns is wrong!**

### XXXCandles: Timestamp error at: XXX. Import blocked"
The csv file XXXCandles has no proper timestamps. Ensure that the candle interval (`INTERVAL`) in `.env` is set
correctly. If this does not solve the problem, the `csv`file has inconsistent timestamp intervals.

### Could not connect to database! Sleeping 5 seconds
Either the `DATABASE_URL` is incorrect or the database is not online. Ensure that the database container is running by
using `docker ps`. See step 1 in the section `Using the Datapump`.
