import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import numpy as np
import copy
import logging

logging.basicConfig(level=logging.INFO, filename="py.log",filemode="w")

# Function to calculate statistics
def calculate_statistics(strategy_actions, ohlc_data, mode='close'):

    """
    Calculate PnL and various statistics for a given strategy.
    
    :param strategy_actions: A DataFrame where each column represents strategy actions for a different instrument
    :param ohlc_data: A DataFrame containing OHLC data with columns 'open', 'high', 'low', 'close'
    :param mode: 'close' for trading at close price, 'average' for trading at average price
    :return: A DataFrame with statistics for each strategy
    """
    results = {}
    
    for strategy_name, actions in strategy_actions.items():
        # Initialize variables
        pnl = []
        position = 0
        position_flips = 0
        holding_periods = []
        current_holding_period = 0
        cash = 0
        volume_traded = 0
        max_drawdown = 0
        max_value = 0
        
        # Simulate each action
        for i in range(len(ohlc_data)):
            price = ohlc_data['close'][i] if mode == 'close' else (ohlc_data['high'][i] + ohlc_data['low'][i]) / 2
            action = actions[i]
            
            if action != 0:
                # Calculate transaction cost
                transaction_value = action * price
                volume_traded += abs(action) * price
                
                # Update PnL and cash
                cash -= transaction_value
                position += action
                
                # Track holding periods
                if current_holding_period > 0 and np.sign(action) != np.sign(position):
                    position_flips += 1
                    holding_periods.append(current_holding_period)
                    current_holding_period = 0
                current_holding_period += 1

            # Calculate current portfolio value
            current_value = cash + position * price
            pnl.append(current_value)
            
            # Update max drawdown
            max_value = max(max_value, current_value)
            drawdown = max_value - current_value
            max_drawdown = max(max_drawdown, drawdown)
        
        # Finalize holding periods
        if current_holding_period > 0:
            holding_periods.append(current_holding_period)
        
        # Calculate statistics
        pnl_series = pd.Series(pnl)
        returns = pnl_series.pct_change().dropna()
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() != 0 else np.nan
        sortino_ratio = returns.mean() / returns[returns < 0].std() * np.sqrt(252) if returns[returns < 0].std() != 0 else np.nan
        
        # Store results
        results[strategy_name] = {
            'PnL': pnl[-1],
            'Traded Volume': volume_traded,
            'Sharpe Ratio': sharpe_ratio,
            'Sortino Ratio': sortino_ratio,
            'Max Drawdown': max_drawdown,
            'Average Holding Time': np.mean(holding_periods) if holding_periods else 0,
            'Position Flips': position_flips
        }
    
    return pd.DataFrame(results).T

# Sample usage with dummy data

def calculate_strategies(data):
    # Create dummy OHLC data
    ohlc_data = pd.DataFrame(data, index=data.index)
    # Create dummy strategy actions
    strategy_actions = pd.DataFrame({
        'Strategy 1': np.random.randint(-10000, 10000, size=data.shape[0]),  # Buy/Sell contracts
        'Strategy 2': np.random.randint(-5000, 5000, size=data.shape[0])  # Another strategy
    }, index=copy.deepcopy(data.index))

    # Run the simulator
    results = calculate_statistics(strategy_actions, ohlc_data, mode='close')

    # Adding the Perfect Future Knowledge strategy to the strategy_actions DataFrame

    def create_perfect_strategy(ohlc_data):
        """
        Creates a strategy that knows the future.
        Buys if the next close price is higher than the current, sells if lower.
        
        :param ohlc_data: A DataFrame containing OHLC data with 'close' column.
        :return: A Series representing the actions of the perfect strategy.
        """
        perfect_actions = []

        # Iterate over the OHLC data
        for i in range(len(ohlc_data) - 1):
            if ohlc_data['close'].iloc[i + 1] > ohlc_data['close'].iloc[i]:
                perfect_actions.append(1000)  # Buy 1000 contracts if the next price is higher
            elif ohlc_data['close'].iloc[i + 1] < ohlc_data['close'].iloc[i]:
                perfect_actions.append(-1000)  # Sell 1000 contracts if the next price is lower
            else:
                perfect_actions.append(0)  # Do nothing if the price is the same

        perfect_actions.append(0)  # No action on the last candle, as there is no future data

        return pd.Series(perfect_actions, index=ohlc_data.index)

    # Assuming ohlc_data is already created and available
    perfect_strategy_actions = create_perfect_strategy(ohlc_data)

    # Add the perfect strategy to the strategy_actions DataFrame
    strategy_actions['Perfect Strategy'] = perfect_strategy_actions

    # Now run the simulator with all three strategies
    results = calculate_statistics(strategy_actions, ohlc_data, mode='close')

    # Display the results
    logging.info(results)
