import logging
import numpy as np
from .utils import *
from .agents.DQN import *


def hold():
    logging.info('Hold')

def buy(agent, risk, stock_prices, t):
    num = int(risk // stock_prices[t])

    agent.balance -= (stock_prices[t] * num)
    for i in range(0, num):
        agent.inventory.append(stock_prices[t])
    agent.buy_dates.append(t)
    logging.info('Buy:  ${:.2f} - Num: {}'.format(stock_prices[t], num))

def sell(agent, risk, stock_prices, t):
    num = int(risk // stock_prices[t])
    profit = 0

    # agent.balance += (stock_prices[t] * num)
    for i in range(0, num):
        if len(agent.inventory) == 0:
            break
        bought_price = agent.inventory.pop(0)
        agent.balance += (stock_prices[t])
        profit += (stock_prices[t] - bought_price)

    global reward
    reward = profit
    agent.sell_dates.append(t)
    logging.info('Sell: ${:.2f} | Profit: ${:.2f} - Num: {}'.format(stock_prices[t], profit, num))
    return reward


def startBacktest(initial_balance, model="DQN_ep10", stock_name='BA_2020'):
    model_to_load = model
    model_name = model_to_load.split('_')[0]

    window_size = 10 #model is trained on window size 10, basically 10 prices before predicting next, cant change now.
    action_dict = {0: 'Hold', 1: 'Buy', 2: 'Sell'}

    logging.basicConfig(filename=f'DQN/logs/{model_name}_evaluation_{stock_name}.log', filemode='w',
                        format='[%(asctime)s.%(msecs)03d %(filename)s:%(lineno)3s] %(message)s', 
                        datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)

    agent = Agent(state_dim=window_size+3, balance=initial_balance, is_eval=True, model_name=model_to_load)
    stock_prices = stock_close_prices(stock_name)
    trading_period = len(stock_prices) - 1
    state = generate_combined_state(0, window_size, stock_prices, agent.balance, len(agent.inventory))
    
    risk = (5/100) * agent.balance
    maxDD = (50/100) * agent.balance

    for t in range(1, trading_period + 1):

        actions = agent.model.predict(state)[0]
        action = agent.act(state)

        next_state = generate_combined_state(t, window_size, stock_prices, agent.balance, len(agent.inventory))
        previous_portfolio_value = len(agent.inventory) * stock_prices[t] + agent.balance
        
        profit = 0
        # execute position
        logging.info(f'Step: {t}')
        if action != np.argmax(actions): 
            logging.info(f"\t\t'{action_dict[action]}' is an exploration.")
        if action == 0: 
            hold() # hold
        if action == 1 and maxDD > stock_prices[t]: 
            buy(agent, risk, stock_prices, t) # buy
        if action == 2 and len(agent.inventory) > 0: 
            profit = sell(agent, risk, stock_prices, t) # sell

        current_portfolio_value = len(agent.inventory) * stock_prices[t] + agent.balance
        agent.return_rates.append(((current_portfolio_value - previous_portfolio_value) / previous_portfolio_value)*100)
        agent.portfolio_values.append(current_portfolio_value)
        agent.profits.append(profit)
        state = next_state

        

    if len(agent.inventory) > 0:
        for stock in agent.inventory:
            sell(agent, risk, stock_prices, -1)

        agent.sell_dates.append(t)
        # agent.return_rates.append((current_portfolio_value - previous_portfolio_value) / previous_portfolio_value)
        # agent.portfolio_values.append(current_portfolio_value)
        agent.profits.append(profit)

    print(agent.inventory)

    portfolio_return = evaluate_portfolio_performance(agent, logging)

    return agent