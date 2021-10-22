from empyrical.stats import annual_return
import numpy as np
import pandas as pd
from empyrical import sharpe_ratio
from matplotlib import pyplot as plt


class Portfolio:
    def __init__(self, balance=50000):
        self.initial_portfolio_value = balance
        self.balance = balance
        self.inventory = []
        self.return_rates = []
        self.portfolio_values = [balance]
        self.buy_dates = []
        self.sell_dates = []
        self.profits = []

    def reset_portfolio(self):
        self.balance = self.initial_portfolio_value
        self.inventory = []
        self.return_rates = []
        self.portfolio_values = [self.initial_portfolio_value]

        
def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def stock_close_prices(key):
    '''return a list containing stock close prices from a .csv file'''
    prices = []
    lines = open("DQN/data/" + key + ".csv", "r").read().splitlines()
    for line in lines[1:]:
        prices.append(float(line.split(",")[4]))
    return prices


def generate_price_state(stock_prices, end_index, window_size):
    '''
    returns prices smushed by sigmoid 0 to 1 of all window size number of prices
    '''
    start_index = end_index - window_size
    if start_index >= 0:
        period = stock_prices[start_index:end_index+1]
    else: # if end_index cannot suffice window_size, pad with prices on start_index
        period = -start_index * [stock_prices[0]] + stock_prices[0:end_index+1]
    return sigmoid(np.diff(period))


def generate_portfolio_state(stock_price, balance, num_holding):
    '''logarithmic values of stock price, portfolio balance, and number of holding stocks'''
    return [np.log(stock_price), np.log(balance), np.log(num_holding + 1e-6)]


def generate_combined_state(end_index, window_size, stock_prices, balance, num_holding):
    '''
    returns smushed value of all <window size> prices + portfolio state(price, balance, inventory)
    '''
    prince_state = generate_price_state(stock_prices, end_index, window_size)
    portfolio_state = generate_portfolio_state(stock_prices[end_index], balance, num_holding)
    return np.array([np.concatenate((prince_state, portfolio_state), axis=None)])


def average_interest_rate():
    #returns average mutual funds per annum 6 to 9% as per google
    #so return per candle of missed oppurtunity will be
    return 0.0003


def maximum_drawdown(portfolio_values):
    end_index = np.argmax(np.maximum.accumulate(portfolio_values) - portfolio_values)
    if end_index == 0:
        return 0
    beginning_iudex = np.argmax(portfolio_values[:end_index])
    return (portfolio_values[end_index] - portfolio_values[beginning_iudex]) / portfolio_values[beginning_iudex]


def evaluate_portfolio_performance(agent, logger):
    portfolio_return = agent.portfolio_values[-1] - agent.initial_portfolio_value
    logger.info("--------------------------------")
    logger.info('Portfolio Value:        ${:.2f}'.format(agent.portfolio_values[-1]))
    logger.info('Portfolio Balance:      ${:.2f}'.format(agent.balance))
    logger.info('Portfolio Stocks Number: {}'.format(len(agent.inventory)))
    logger.info('Total Return:           ${:.2f}'.format(portfolio_return))
    logger.info('Mean/Daily Return Rate:  {:.3f}%'.format(np.mean(agent.return_rates) * 100))
    logger.info('Sharpe Ratio adjusted with Treasury bond daily return: {:.3f}'.format(sharpe_ratio(np.array(agent.return_rates)), risk_free=average_interest_rate()))
    logger.info('Maximum Drawdown:        {:.3f}%'.format(maximum_drawdown(agent.portfolio_values) * 100))
    logger.info("--------------------------------")
    return portfolio_return



def buy_and_hold_benchmark(stock_name, agent):
    df = pd.read_csv('DQN/data/{}.csv'.format(stock_name))
    dates = df['Date']
    num_holding = agent.initial_portfolio_value // df.iloc[0, 4]
    balance_left = agent.initial_portfolio_value % df.iloc[0, 4]
    buy_and_hold_portfolio_values = df['Close']*num_holding + balance_left
    buy_and_hold_return = buy_and_hold_portfolio_values.iloc[-1] - agent.initial_portfolio_value
    return dates, buy_and_hold_portfolio_values, buy_and_hold_return