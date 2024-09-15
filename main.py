import pandas as pd
from candle import draw_candles as draw
from candle import prepare_data
from strategies import calculate_strategies as calc

if __name__ == '__main__':
    print('Choose which graph do you want to generate and enter the path to dataframe.')
    print('for example: src/md_sim/bbo_dogeusdt.csv')
    path = input()
    data = pd.read_csv(path)
    ohlc = prepare_data(data)
    for i in range(10):
        calc(ohlc)
    draw(ohlc)
    
