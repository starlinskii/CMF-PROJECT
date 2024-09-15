import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np



# Define function to create OHLC candles
def generate_ohlc(data, T):
    # Resample the data to create OHLC candles
    ohlc_data = data['bid_price'].resample(f'{T}L').ohlc()
    ohlc_data['volume'] = data['bid_amount'].resample(f'{T}L').sum()
    return ohlc_data.dropna()  # Drop any NaN values

def prepare_data(data):

    data['local_timestamp'] = pd.to_datetime(data['local_timestamp'], unit='us')  # Adjust as needed

    # Set the index for easier resampling
    data.set_index('local_timestamp', inplace=True)

    # Example usage:
    print('set time in ms: ')
    T = int(input())  # Set the desired time window in milliseconds (e.g., 60 seconds)
    return generate_ohlc(data, T)


def draw_candles(ohlc_candles):

    # Plotting using mplfinance without volume
    mpf.plot(
        ohlc_candles,
        type='line',
        style='charles',
        title='OHLC Candlestick Chart',
        ylabel='Price',
        datetime_format='%Y-%m-%d %H:%M:%S',
        tight_layout=True
    )

    plt.show()
    return ohlc_candles
