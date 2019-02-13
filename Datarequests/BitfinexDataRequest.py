import http.client
import csv
import sys
import logging
from time import sleep

conn = http.client.HTTPSConnection("api.bitfinex.com")
sys.setrecursionlimit(10000)

end_time = 1548158400000
pairs = ["tETCBTC", "tETCUSD", "tETHBTC", "tETHUSD", "tIOTBTC", "tIOTETH", "tIOTUSD", "tLTCBTC", "tLTCUSD", "tNEOUSD",
         "tOMGBTC", "tOMGETH", "tOMGUSD", "tQTMBTC", "tQTMETH", "tQTMUSD", "tTRXUSD", "tXMRBTC", "tXMRUSD", "tXRPBTC",
         "tXRPUSD", "tZECBTC", "tZECUSD", "tZRXUSD"]
headers = {'cache-control': "no-cache", 'postman-token': "a82c86e7-5a5e-f260-e77e-e93dd9a02964", 'user-agent': "random"}
delay = 3.5
base = 5 * 60000
logger = logging.getLogger("Cleaner")


def get_csv(pair: str):
    pairname = pair[1:]
    return open(f"data/{pairname}_Bitfinex5MCandles.csv", 'a', newline='')


def get_data(pair: str, time: int) -> None:
    """
  Get the data for specified pair with specified end time
  :param pair: Pair to fetch data for
  :param time: End time use in the request
  """

    conn.request("GET", "/v2/candles/trade:5m:" + pair + "/hist?end=" + str(time) + "&limit=1000", headers=headers)
    res = conn.getresponse()
    # Candle format: StartTS, Open, Close, High, Low
    data = res.read().decode("utf-8")
    list_data = eval(data)

    # if list_data[0] == "error":
    #     logger.error(f"Error received from Bitfinex: {list_data[2]}. Delaying and retrying")
    #     sleep(6000)
    #     get_data(pair, time)

    """
    Checks if the fetched list data is larger than 1. Because we are using the end time, the request will always return
    1 candle.
    """
    if len(list_data) > 1:
        # Convert to matrix array
        for i, x in enumerate(list_data):
            for j, y in enumerate(x):
                try:
                    list_data[i][j] = y
                except TypeError:
                    print("d")
        # Get CSV file
        writer = csv.writer(get_csv(pair), delimiter=",")
        writer.writerows(sorted(list_data, reverse=True))

        new_time = list_data[len(list_data) - 1][0] - base

        # Don't get kicked out
        sleep(delay)

        # Recursion
        get_data(pair, new_time)
    else:
        print(list_data)
        print(f"Fetching completed for {pair}")


def main() -> None:
    """
  Loop over pairs and fetch data
  """
    for pair in pairs:
        print(f"Fetching started for {pair}")
        get_data(pair, end_time)


if __name__ == "__main__":
    # Set logging config
    logging.basicConfig()
    logger.setLevel(logging.INFO)

    # Enable debugging
    # logger.setLevel(logging.DEBUG)

    main()
