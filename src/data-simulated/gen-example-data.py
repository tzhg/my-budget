#!/bin/bash

import os, math
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm, uniform
from datetime import datetime, timedelta

# Current directory
dirname = os.path.dirname(os.path.abspath(__file__))

input_date_format = "%d/%m/%Y"

exp_cats = ["Housing", "Food", "Utilities", "Health", "Shopping", "Leisure", "Other"]
inc_cats = ["Salary", "Other"]

# Parameters of normal distribution for irregular expenses/income values
# exp_multi increases expenses based on available cash (per thousand)
exp_mean = [100, 12, 50, 50, 50, 50, 100]
exp_multi = [0, 3, 2, 5, 15, 40, 0]
exp_sd = [50, 0, 25, 50, 500, 500, 100]
inc_mean = [0, 200]
inc_sd = [0, 200]
# Expected days in year with an irregular expense, for each category
exp_days = [2, 100, 10, 15, 15, 15, 15]
inc_days = [0, 5]

svgb_mean = 0
svgb_multi = 20
svgb_sd = 50
svgb_days = 3

svgs_mean = 0
svgs_multi = 20
svgs_sd = 50
svgs_days = 1

error_mean = 0
error_sd = 5
error_days = 20
check_days = 10

# Regular monthly expenses/income
exp_monthly = [1700, 0, 300, 0, 0, 0, 0]
inc_monthly = [3500, 0]

# Starting and (non-inclusive) end date
init_date = "2013-01-01"
end_date = "2023-01-01"

# Number of days of data
no_days = 365

init_debt = 20000
# Proportion of principal of debt paid off each month
debt_p = 0.01
# Interest rate
debt_r = 0.01

# Portfolio of savings assets in simulation
# Columns: name, unit value, quantity held, category, description
portfolio = [
    ["a0", 1, 0, "financial", "Savings account"],
    ["a1", 1, 0, "financial", "Apple stock"],
    ["a2", 1, 0, "financial", "Pension"],
    ["d0", -init_debt, 1, "debt", "Loan"],
    ["r0", 5000, 1, "real", "Jewellery"]]

asset_growth_mean = 0.001
asset_growth_sd = 0.05

init_cash = 7000

cash_cat = ["Cash", "Bank account"]
cash_cat_prop = [0.4, 0.6]

date = datetime.strptime(init_date, "%Y-%m-%d")
cash = init_cash


def spend(cat, value):
    global cash, date

    value = min(value, cash)
    cash -= value

    f_date = datetime.strftime(date, input_date_format)

    with open(os.path.join(dirname, "expenses-input.csv"), "a") as file:
        file.write(f"{f_date},{exp_cats[cat]},{value:.2f}\n")


def earn(cat, value):
    global cash, date

    cash += value

    f_date = datetime.strftime(date, input_date_format)

    with open(os.path.join(dirname, "income-input.csv"), "a") as file:
        file.write(f"{f_date},{value:.2f}\n")

# total_value = value of asset gained
def savings(index, type, total_value):
    global cash, date, portfolio

    if type == "S":
        total_value *= -1

    total_value = min(total_value, cash)

    unit_value = portfolio[index][1]

    quantity = max(-portfolio[index][2], total_value / unit_value)

    portfolio[index][2] += quantity

    total_value = quantity * unit_value

    cash -= total_value

    f_date = datetime.strftime(date, input_date_format)

    with open(os.path.join(dirname, "savings-input.csv"), "a") as file:
        file.write(f"{f_date},{type},{portfolio[index][0]},{abs(quantity)},{unit_value}\n")


def profit_loss(index, value):
    f_date = datetime.strftime(date, input_date_format)

    with open(os.path.join(dirname, "profit-loss-input.csv"), "a") as file:
        file.write(f"{f_date},{portfolio[index][0]},{value}\n")


def cash_snapshot():
    global cash, date

    with open(os.path.join(dirname, "cash-input.csv"), "a") as file:
        cash_comp = [cash_cat_prop[i] * cash for i, x in enumerate(cash_cat)]

        cash_comp[-1] = cash - sum(cash_comp[:-1])

        st = " + ".join([f"{x:.2f} ({cash_cat[i]})" for i, x in enumerate(cash_comp)])

        f_date = datetime.strftime(date, input_date_format)

        file.write(f"{f_date}, {st}\n")


with open(os.path.join(dirname, "expenses-input.csv"), "w") as file:
    file.write("date,category,value\n")
with open(os.path.join(dirname, "income-input.csv"), "w") as file:
    file.write("date,value\n")
with open(os.path.join(dirname, "savings-input.csv"), "w") as file:
    file.write("date,type,name,quantity,value\n")
with open(os.path.join(dirname, "savings-info.csv"), "w") as file:
    file.write("name,category,description\n")
with open(os.path.join(dirname, "profit-loss-input.csv"), "w") as file:
    file.write("date,name,value\n")
with open(os.path.join(dirname, "cash-input.csv"), "w") as file:
    file.write("date,cash\n")

for i in range(len(portfolio)):
    with open(os.path.join(dirname, "savings-info.csv"), "a") as file:
        file.write(f"{portfolio[i][0]},{portfolio[i][3]},{portfolio[i][4]}\n")

    if portfolio[i][3] == "financial":
        with open(os.path.join(dirname, f"assets/{portfolio[i][0]}.csv"), "w") as file:
            file.write("date,value\n")

# Initial cash
with open(os.path.join(dirname, "cash-input.csv"), "a") as file:
    cash_snapshot()

# Initial savings
for i in range(len(portfolio)):
    f_date = datetime.strftime(date, input_date_format)

    with open(os.path.join(dirname, "savings-input.csv"), "a") as file:
        file.write(f"{f_date},I,{portfolio[i][0]},{portfolio[i][2]},{portfolio[i][1]}\n")

# Iterates through each day
while date < datetime.strptime(end_date, "%Y-%m-%d"):
    # Updates asset prices
    for asset in portfolio:
        if asset[3] == "financial":
            asset[1] += round(np.exp(norm.rvs(asset_growth_mean, asset_growth_sd)), 2)
            with open(os.path.join(dirname, f"assets/{asset[0]}.csv"), "a") as file:
                f_date = datetime.strftime(date, input_date_format)
                file.write(f"{f_date},{asset[1]}\n")

    # Introduces errors
    rv = uniform.rvs()
    if rv < error_days / 365:
        cash += norm.rvs(error_mean, error_sd).round(2)

    # Checks remaining cash
    rv = uniform.rvs()
    if rv < check_days / 365:
        cash_snapshot()

    # Regular monthly expenses/income (e.g. rent, salary)
    if date.day == 1:
        for i, x in enumerate(inc_monthly):
            earn(i, x)
        for i, x in enumerate(exp_monthly):
            spend(i, x)

    # Irregular income
    rv_u = uniform.rvs(size=len(inc_cats))
    rv_n = norm.rvs(inc_mean, inc_sd, size=len(inc_cats)).round(2)
    for i in range(len(inc_cats)):
        if rv_u[i] < inc_days[i] / 365:
            value = max(0, rv_n[i])
            earn(i, value)

    # Irregular expenses
    rv_u = uniform.rvs(size=len(exp_cats))
    mu = np.array(exp_mean) + cash * exp_multi[i] / 1000
    rv_n = norm.rvs(mu, exp_sd, size=len(exp_cats)).round(2)
    for i in range(len(exp_cats)):
        if rv_u[i] < exp_days[i] / 365:
            value = max(0, rv_n[i])
            spend(i, value)

    # Buying savings
    rv_u = uniform.rvs(size=len(portfolio))
    mu = svgb_mean + cash * svgb_multi / 1000
    rv_n = norm.rvs(mu, svgb_sd, size=len(portfolio)).round(2)
    debt = -1
    for i in range(len(portfolio)):
        if portfolio[i][3] == "debt" and portfolio[i][1] * portfolio[i][2] < 0:
            debt = i
    for i in range(len(portfolio)):
        if portfolio[i][3] == "financial":
            if rv_u[i] < svgb_days / 365:
                value = max(0, rv_n[i])
                if debt == -1:
                    savings(i, "B", value)
                else:
                    savings(debt, "S", -value)

    # Selling savings
    rv_u = uniform.rvs(size=len(portfolio))
    mu = svgs_mean + cash * svgs_multi / 1000
    rv_n = norm.rvs(mu, svgs_sd, size=len(portfolio)).round(2)
    for i in range(len(portfolio)):
        if portfolio[i][3] == "financial":
            if rv_u[i] < svgs_days / 365:
                value = max(0, rv_n[i])
                savings(i, "S", value)

    # Pays of debt
    if date.day == 1:
        for i in range(len(portfolio)):
            if portfolio[i][3] == "debt" and portfolio[i][1] * portfolio[i][2] < 0:
                savings(i, "S", -init_debt * debt_p)
                profit_loss(i, portfolio[i][1] * portfolio[i][2] * debt_r)

    date = date + timedelta(days=1)
