import mesa
import numpy as np
from mesa.datacollection import DataCollector
np.random.seed(0)

class Household(mesa.Agent):
    """An agent with wealth, income and housing needs"""
    def __init__(self, unique_id, model, income_avg,income_std,wealth_avg,wealth_std,housing_stock):
        super().__init__(unique_id, model)

        self.wealth = np.random.normal(wealth_avg,wealth_std)
        # Only positive incomes
        self.income = abs(np.random.normal(income_avg,income_std))
        self.agent_type = "displaced"
        self.houses = []
        self.rent_payment = None
        self.leased_house = None
        self.housing_stock = housing_stock 


    def buy_house(self):
        """Buy a house and add it to the list of owned houses"""
        for house in self.housing_stock:
            if house.status == "vacant" and house.price < self.wealth:
                house.status = "owned"
                house.owner = self.unique_id
                self.wealth -= house.price 
                self.houses.append(house.id)
                break

    def rent_out_house(self):
        """If you have multiple houses, rent them out"""
        for house in self.housing_stock:
            # Match additional house to housing stock
            if house.id == self.houses[-1]:
                house.status = "for_rent"

    def rent_house(self):
        """Rent a house"""
        for house in self.housing_stock:
            if house.status == "for_rent" and house.rent < 0.3*self.income:
                house.status = "rented"
                self.agent_type = "renter"
                self.rent_payment = house.rent
                self.leased_house = house.id
    
    def collect_rent(self):
        """If you have rented houses, collect the rent payment"""
        if self.agent_type == "investor":
            for house in self.housing_stock:
                if house.status == "rented" and house.id in self.houses:
                    self.wealth += house.rent

    def step(self):
        # print(f"ID#: {self.unique_id} is a {self.agent_type} with income: {self.income:2f} and wealth {self.wealth:2f}")
        # Generate income every year    
        self.wealth += self.income

        self.income = self.income*1.05
        # Determine agent type
        if len(self.houses) > 1:
            self.agent_type = "investor"
            # Rent house if you have multilple
            self.rent_out_house()

        if len(self.houses) == 1:
            self.agent_type = "owner"

        # Try to buy a house
        self.buy_house()

        # If renting, remove rent from wealth
        if self.agent_type == "renter":
            self.wealth -= self.rent_payment
        
        # If too expensive, try to rent a house
        if self.agent_type == "displaced":
            self.rent_house()


class House():
    """"A class representing a house asset."""
    next_id = 1
    def __init__(self,h_price, h_price_std, h_rent,h_rent_std):
        # Assign the next available id to the current instance
        self.id = House.next_id
        # Increment the next available id for the next instance
        House.next_id += 1
        self.price = np.random.normal(h_price,h_price_std)
        self.quality = np.random.uniform(1,10)
        self.rent = np.random.normal(h_rent,h_rent_std)
        self.owner = None
        self.status = "vacant"

class HousingMarket(mesa.Model):
    """"Model with Household Agents"""
    def __init__(self, N,income_avg,income_std,wealth_avg,wealth_std,housing_stock):
        self.num_agents = N
        self.schedule = mesa.time.RandomActivation(self)
        self.income_avg = income_avg
        self.income_std = income_std
        self.wealth_avg = wealth_avg
        self.wealth_std = wealth_std
        self.housing_stock = housing_stock

       # Custom agent reporter function to calculate the length of the 'houses' attribute
        def count_houses(agent):
            return len(agent.houses)

        # Initialize DataCollector with the custom agent reporter
        self.datacollector = DataCollector(agent_reporters={"Wealth": "wealth", "AgentType": "agent_type", "NumHouses": count_houses})
            
        # Create agents
        for i in range(self.num_agents):
            a = Household(i, self,self.income_avg,self.income_std,self.wealth_avg,self.wealth_std, self.housing_stock)
            self.schedule.add(a)

    def step(self):
        # Call moodel and move it one period forward
        self.schedule.step()
        # Collect agent-level data at each step
        self.datacollector.collect(self)
        