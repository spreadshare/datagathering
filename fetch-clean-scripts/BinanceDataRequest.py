import http.client
import csv
import sys
from time import sleep

conn = http.client.HTTPSConnection("api.binance.com")
sys.setrecursionlimit(10000)

end_time = 1548158400000
pairs = ["ADABTC", "ADAETH", "ADAUSDT", "AEBTC", "AEETH", "BNBBTC", "BNBETH", "BNBUSDT", "CMTBTC", "CMTETH", "DGDBTC",
         "DGDETH", "ETCETH", "HOTBTC", "HOTETH", "ICXBTC", "ICXETH", "ICXUSDT", "IOSTBTC", "IOSTETH", "LSKBTC",
         "LSKETH", "LTCETH", "NEOBTC", "NEOETH", "NPXSBTC", "NPXSETH", "ONTBTC", "ONTETH", "ONTUSDT", "TRXBTC",
         "TRXETH", "VETBTC", "VETETH", "VETUSDT", "XEMBTC", "XEMETH", "XLMBTC", "XLMETH", "XLMUSDT", "XMRETH", "XRPETH",
         "ZECETH", "ZRXBTC", "ZRXETH"]

headers = {'cache-control': "no-cache", 'postman-token': "a82c86e7-5a5e-f260-e77e-e93dd9a02964", 'user-agent': "random"}

# Add delay between requests to prevent being kicked out
delay = 0.1


def get_csv(pair: str):
    """
    Get the csv file for a given pair.

    :param pair: Trading pair concerned in the csv
    :return: CSV Stream
    """
    return open(f"data/{pair}_Binance5MCandles.csv", 'a', newline='')


def get_data(pair: str, time: int) -> None:
    """
    Get the data for specified pair with specified end time.

    :param pair: Pair to fetch data for
    :param time: End time use in the request
    """
    conn.request("GET", "/api/v1/klines?symbol=" + pair + "&interval=5m&endTime=" + str(time) + "&limit=500",
                 headers=headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    list_data = eval(data)

    """
    Checks if the fetched list data is larger than 1. Because we are using the end time, the request will always return
    1 candle.
    """
    if len(list_data) > 1:
        # Convert to matrix array
        for i, x in enumerate(list_data):
            for j, y in enumerate(x):
                list_data[i][j] = y

        # Get CSV file
        writer = csv.writer(get_csv(pair), delimiter=",")
        writer.writerows(sorted(list_data, reverse=True))

        # Set new time (the closing time of the oldest candle)
        new_time = list_data[0][6]

        # Don't get kicked out
        sleep(delay)

        # Recursion
        get_data(pair, new_time)
    else:
        print(list_data)
        print(f"Fetching completed for {pair}")


def main() -> None:
    """Loop over pairs and fetch data."""
    for pair in pairs:
        print(f"Fetching started for {pair}")
        get_data(pair, end_time)


if __name__ == "__main__":
    main()
