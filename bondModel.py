import pandas as pd
import numpy as np
from datetime import datetime
import math


def get_maturity_list(bond, period):
    list_maturity = []

    for i in range(0, period):
        if ((i + 1) % bond["maturity"].values.astype(int)[0]) == 0:
            list_maturity.append("yes")
        else:
            list_maturity.append("no")
    
    return list_maturity

def get_intrest_list(bond, period, interest_list, list_maturity):
    list_intrest = []
    interest_index = 0    

    new_month = 0
    for i in range(0, period):
        if i % 12 == 0:
            interest = interest_list[interest_index]
            interest_index += 1
        
        if interest_index == 1:
            list_intrest.append(round(interest, 4))
        
        elif list_maturity[i - 1] == "yes" or new_month != 0:
            list_intrest.append(round(interest, 4))
            new_month += 1
            
            if new_month == 12:
                new_month = 0
            
        else:
            list_intrest.append(round(bond["margin"].values.astype(float)[0] + interest, 4))
            
    return list_intrest

def get_gross_value_list(bond, period, base_value_list, interest_list):
    
    try:
        interest_payment = bond["interest_payment"].values.astype(int)[0]
    except ValueError:
        interest_payment = bond["maturity"].values.astype(int)[0]
    
    list_gross = []
    for i in range(0, period):
        if (i + 1) % interest_payment != 0:
            ifPayment = (i + 1) % interest_payment
        else:
            ifPayment = interest_payment
        
        list_gross.append( round(base_value_list[i] * (1 + interest_list[i] * ifPayment / 12), 2))
    
    return list_gross

def get_cost_of_early_buyout(bond, period, base_value_list, list_gross, bont_count_list = ""):
    maturity = bond["maturity"].values.astype(int)[0]
    
    try:
        unchanged_value_early_buyout_moths = bond["unchanged_value_early_buyout_moths"].values.astype(int)[0]
    except ValueError:
        unchanged_value_early_buyout_moths = maturity
    
    cost_of_early_buyout_list = []
    
    if not bont_count_list:
        bont_count_list = [base_value_list[0] / 100] * period
    
    for i in range(0, period):
        if (i + 1) % maturity == 0:
            cost_of_early_buyout_list.append(0)
            
        elif ((i + 1) % maturity < maturity) and ((i + 1) % maturity <= unchanged_value_early_buyout_moths):
            cost_of_early_buyout_list.append(round(min(bond["cost_of_early_buyout_PLN"].values.astype(float)[0] * bont_count_list[i], list_gross[i] - base_value_list[i]), 2))
            
        else:
            cost_of_early_buyout_list.append(round(bond["cost_of_early_buyout_PLN"].values.astype(float)[0] * bont_count_list[i], 2))
            
    return cost_of_early_buyout_list



def get_paycheck(bond, period, base_value_list, list_gross, list_maturity, end_moth_buyout, tax):    
    try:
        interest_payment = bond["interest_payment"].values.astype(int)[0]
    except ValueError:
        return [0] * period
    
    nominal_value = base_value_list
    balance_list = [0]
    
    for i in range(0, period):
        if list_maturity[i] == "yes" and i > 0:
            balance_list.append(round(end_moth_buyout[i] - math.floor(end_moth_buyout[i]  / bond["exchange_price_PLN"].values.astype(float)[0]) * bond["exchange_price_PLN"].values.astype(float)[0], 2))
        elif (i + 1) % interest_payment == 0:
            balance_list.append(round((list_gross[i] - nominal_value[i]) * (1 - tax), 2))
        else:
            balance_list.append(0)
        
    balance_list.pop(0)
    return balance_list

def get_bond_count(bond, period, cost, list_maturity, end_moth_buyout, balance):
    try:
        exchange = bond["exchange_price_PLN"].values.astype(float)[0]
    except ValueError:
        exchange = 100.0
    
    bond_count_list = [cost / 100]
    list_maturity = list_maturity
    
    for i in range(0, period):
        if list_maturity[i] == "yes" and i > 0:
            bond_count_list.append(round(math.floor(end_moth_buyout[i] / exchange) + math.floor( (balance[i]) / 100), 2))

        else:
            bond_count_list.append(bond_count_list[-1])
    
    bond_count_list.pop(0)
    return bond_count_list


def get_total(bond, period, balance_list, end_moth_buyout):
    total = []
    balance_list = [0.0] + balance_list
    maturity = bond["maturity"].values.astype(int)[0]
    
    for i in range(0, period):
        ifmod = 0
        if i % maturity == 0:
            ifmod = math.floor(balance_list[i -1] / 100) * 100

        total.append(round(balance_list[i -1] - ifmod + end_moth_buyout[i],2))

    balance_list.pop(0)
    return total


def get_balance(period, paycheck, list_maturity):
    balance_list = [0]
    
    for i in range(0, period):
        ifyes = 0
        if list_maturity[i - 1] == "yes" and i > 0:
            ifyes = math.floor(balance_list[-1] / 100) * 100
        
        balance_list.append(round(balance_list[-1] - ifyes  + paycheck[i], 2))
        
    balance_list.pop(0)
    return balance_list

def get_gross_value_list(bond, period, base_value_list, interest_list):
    interest_capitalization = -1
    try:
        interest_payment = bond["interest_payment"].values.astype(int)[0]
    except ValueError:
        interest_payment = bond["maturity"].values.astype(int)[0]
        interest_capitalization	= bond["interest_capitalization"].values.astype(int)[0]
    
    list_gross = []
    for i in range(0, period):
        if (i + 1) % interest_payment != 0 and interest_capitalization == -1:
            ifPayment = (i + 1) % interest_payment
        elif interest_capitalization == -1:
            ifPayment = interest_payment
        elif (i + 1) % interest_capitalization != 0:
            ifPayment = (i + 1) % interest_capitalization
        else:
            ifPayment = 12
        
        list_gross.append( round(base_value_list[i] * (1 + interest_list[i] * ifPayment / 12), 2))
    
    return list_gross


def get_nominalValue(bond, period, list_maturity, bond_count_list, cost, gross_list):
    try:
        interest_capitalization	= bond["interest_capitalization"].values.astype(int)[0]
    except ValueError:
        interest_capitalization = -1
        
    nominal_list = [cost]
    list_maturity = ["no"] + list_maturity
    
    for i in range(0, period):
        if list_maturity[i] == "yes":
            nominal_list.append(bond_count_list[i] * 100)
        else:
            nominal_list.append(nominal_list[-1])
            
        if (i+1) % interest_capitalization == 1 and i > 0 and interest_capitalization != -1:
            nominal_list[i + 1] = gross_list[i - 1]
        
    nominal_list.pop(0)
    
    return nominal_list


def get_end_moth_buyout(bond, period, base_value_list, list_gross, cost_of_early_buyout, tax):
    nominal_value = []
    end_moth_buyout_list = []
    maturity = bond["maturity"].values.astype(int)[0]
    
    try:
        interest_capitalization	= bond["interest_capitalization"].values.astype(int)[0]
        for i in range(0, period):
            if (i + 1) % maturity == 0 or i == 0:
                nominal_value.append(base_value_list[i])
            else:
                nominal_value.append(nominal_value[-1])
                
    except ValueError:
        nominal_value = base_value_list
    
    for i in range(0, period):
        if i == 0:
            end_moth_buyout_list.append(round(nominal_value[i], 2))
        else:
            temp = list_gross[i] - cost_of_early_buyout[i] - (list_gross[i] - nominal_value[i - 1] - cost_of_early_buyout[i]) * tax
            end_moth_buyout_list.append(round(temp, 2))
        
    return end_moth_buyout_list


def get_bond_df(bond, period, predicted_intrest, cost, tax = 0.19):
    base_value = [cost] * period

    maturity_list = get_maturity_list(bond, period)
    intrest_list = get_intrest_list(bond, period, predicted_intrest, maturity_list)
    
    for i in range(0, math.ceil(144 / bond["maturity"].values.astype(int)[0]) + 12):
        gross_list = get_gross_value_list(bond, period, base_value, intrest_list)
        cost_of_early_buyout = get_cost_of_early_buyout(bond, period, base_value, gross_list)
        end_moth_buyout = get_end_moth_buyout(bond, period, base_value, gross_list, cost_of_early_buyout, tax)
        paycheck = get_paycheck(bond, period, base_value, gross_list, maturity_list, end_moth_buyout, tax)
        balance = get_balance(period, paycheck, maturity_list)
        total = get_total(bond, period, balance, end_moth_buyout)
        bond_count = get_bond_count(bond, period, cost, maturity_list, end_moth_buyout, balance)
        base_value = get_nominalValue(bond, period, maturity_list, bond_count, cost, gross_list)
        
        
    df = pd.DataFrame({"maturity" : maturity_list, "intrest" : intrest_list, "base_value" : base_value, "gross_list" : gross_list,
                        "cost_of_early_buyout" : cost_of_early_buyout, "end_moth_buyout" : end_moth_buyout, "paycheck" : paycheck, "balance" : balance,
                        "bond_count" : bond_count, "total" : total})

    return df


def get_inflation_models( inflationList, period = 144, cost = 50000, tax = 0.19):
    
    bonds = pd.read_csv("economic_data/bonds.csv", delimiter=";")

    res = {} 
    for index, row in bonds[bonds["index_pointer"] == "inflation"].iterrows():
        inflation_list = inflationList.copy()
        
        temp = row.to_dict()
        bond = pd.DataFrame([temp]) 
        
        inflation_list = [bond["procent_first_year"].values.astype(float)[0]] + [round(x / 100, 4) for x in inflation_list]

        bond_df = get_bond_df(bond, period, inflation_list, cost, tax)
        res[bond["bond_type"].values.astype(str)[0]] = bond_df
    
    return res