import pandas as pd
import logging

base = 5 * 60000
pairs = [
    "ETCBTC",
    "ETCUSD",
    "ETHBTC",
    "ETHUSD",
    "IOTBTC",
    "IOTETH",
    "IOTUSD",
    "LTCBTC",
    "LTCUSD",
    "NEOUSD",
    "OMGBTC",
    "OMGETH",
    "OMGUSD",
    "QTMBTC",
    "QTMETH",
    "QTMUSD",
    "TRXUSD",
    "XMRBTC",
    "XMRUSD",
    "XRPBTC",
    "XRPUSD",
    "ZECBTC",
    "ZECUSD",
    "ZRXUSD",
]

logger = logging.getLogger("Cleaner")


def get_csv(pair: str):
    """
    Get the csv file for a given pair.

    :param pair: Trading pair concerned in the csv
    :return: CSV Stream
    """
    return open(f"data/{pair}_Bitfinex5MCandles.csv")


def round_timestamp(timestamp):
    """
    Round given timestamp to nearest integer such that i % base == 0.

    :param timestamp: Timestamp to round
    :return: Rounded timestamp
    """
    return int(base * round(float(timestamp) / base))


def insert_missing_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Insert missing timestamps with default of the previous timestamp.

    :param df: DataFrame to adjust
    :return: Adjusted DataFrame
    """
    df_length = df.shape[0]

    # Keep track of rows to be inserted
    new_rows = {}

    # Current index of new row
    new_id = 1 + df_length

    for i in range(0, df_length):
        # Skip first row
        if i == df_length - 1:
            continue

        # Get current, next timestamp (note: earlier timestamps are later in the list)
        timestamp_current = df.iloc[i, 0]
        timestamp_next = df.iloc[i + 1, 0]
        timestamp_diff = timestamp_next - timestamp_current

        # Check if timestamp difference is multiple of base
        if timestamp_diff % base != 0:
            raise ValueError(
                f"Difference between {timestamp_next} and {timestamp_current} is not a multiple of {base}"
            )

        # Calculate the amount of new timestamps to create
        # Example: 600000 --> create 1 new candle
        new_timestamp_count = (timestamp_diff / base) - 1

        if new_timestamp_count < 0:
            raise ValueError(f"Duplicates found or wrong ordering! {timestamp_current}")

        # No new timestamps
        if new_timestamp_count == 0:
            continue

        logger.debug("##########")
        logger.debug(f"Current timestamp : {timestamp_current}")
        logger.debug(f"Next timestamp : {timestamp_next}")
        logger.debug(f"Timestamp to add: {new_timestamp_count}")

        # Add row per missing timestamp (range(1,3+1) -> [1,2,3])
        for x in range(1, int(new_timestamp_count) + 1):
            # Calculate new timestamp
            ts_add = timestamp_current + (base * x)

            logger.debug(f"Timestamp to add : {ts_add}")

            # Add new timestamp and increment id
            new_rows[new_id] = [
                ts_add,
                df.iloc[i, 2],
                df.iloc[i, 2],
                df.iloc[i, 2],
                df.iloc[i, 2],
                0,
            ]
            new_id += 1

    new_data = pd.DataFrame.from_dict(
        new_rows,
        orient="index",
        columns=["OpenTimestamp", "Open", "Close", "High", "Low", "Volume"],
    )

    logger.debug(f"Timestamps added: {len(new_data)}")

    return df.append(new_data, sort=False)


def clean_data(pair):
    """
    Clean data of given pair.

    :param pair: Pair for which to clean data.
    """
    try:
        csv = get_csv(pair)
    except FileNotFoundError:
        logger.error(
            f"Could not find a csv for trading pair {pair}. Skipping this pair"
        )
        return

    # Convert CSV to DataFrame
    dirty = pd.read_csv(
        csv, names=["OpenTimestamp", "Open", "High", "Low", "Close", "Volume"]
    )

    # Set all timestamps to nearest divisible minute
    dirty["OpenTimestamp"] = dirty["OpenTimestamp"].apply(round_timestamp)

    # Remove duplicates
    dirty = dirty.drop_duplicates(subset=["OpenTimestamp"])

    # Sort timestamps from low to high
    dirty = dirty.sort_values(by=["OpenTimestamp"], ascending=True)

    # Insert missing timestamps
    dirty = insert_missing_timestamps(dirty)

    # # Resort as new timestamps have been appended
    dirty = dirty.sort_values(by=["OpenTimestamp"], ascending=True)

    # Sort the columns into ordering the system expects
    dirty = dirty[["OpenTimestamp", "Open", "Close", "High", "Low", "Volume"]]

    # Output to csv
    dirty.to_csv(f"data/cleaned/{pair}.csv", sep=",", encoding="utf-8", index=False)


def main() -> None:
    """Clean data for given."""
    for pair in pairs:
        logger.info("#############################")
        logger.info(f"Starting cleaning on {pair}")
        clean_data(pair)

    logger.info("#############################")


if __name__ == "__main__":
    # Set logging config
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    # Enable debugging
    # logger.setLevel(logging.DEBUG)

    # Clean data
    main()
