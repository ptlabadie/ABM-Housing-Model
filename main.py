from utils import House, Household, HousingMarket
import numpy as np 

np.random.seed(0)
agent_income_avg = 20000
agent_income_std = 2050
agent_wealth_avg = 1000000
agent_wealth_std = 1000000
h_price_avg = 1000000
h_price_std = 250
h_rent_avg = 10000
h_rent_std = 250


# # Add houses to the housing_stock list
housing_stock = []
for i in range(100):
    # Add housing stats here
    housing_stock.append(House(h_price_avg,h_price_std,h_rent_avg,h_rent_std))

# Add agent wealth variables here
model = HousingMarket(200,agent_income_avg,agent_income_std,agent_wealth_avg,agent_wealth_std, housing_stock)
for i in range(30):
    model.step()



agent_data = model.datacollector.get_agent_vars_dataframe().reset_index()


# Group by 'Step' and 'AgentType' and count occurrences
summary_stats = agent_data.groupby(['Step', 'AgentType']).size().reset_index(name='Count')

# Pivot the DataFrame to get 'AgentType' as columns
pivot_table = summary_stats.pivot_table(index='Step', columns='AgentType', values='Count', fill_value=0)



