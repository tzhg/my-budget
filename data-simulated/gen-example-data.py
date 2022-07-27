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
exp_mean = [300, 40, 100, 100, 200, 250, 100]
exp_sd = [100, 20, 60, 120, 250, 400, 100]
inc_mean = [0, 200]
inc_sd = [0, 200]

svg_mean = 0
svg_sd = 500

error_mean = 0
error_sd = 5

# Expected days in year with an irregular expense, for each category
exp_days = [2, 120, 5, 15, 12, 5, 15]
inc_days = [0, 5]
svg_days = 2
check_days = 10
error_days = 20

# Regular monthly expenses/income
exp_monthly = [1700, 0, 500, 150, 0, 100, 0]
inc_monthly = [3500, 0]

# Starting and (non-inclusive) end date
init_date = "2013-01-01"
end_date = "2023-01-01"

# Number of days of data
no_days = 365

# Portfolio of savings assets in simulation
# Columns: name, unit value, quantity held
portfolio = [
    ["a0", 1, 0],
    ["a1", 1, 0],
    ["a2", 1, 0]]

asset_growth_mean = 0.001
asset_growth_sd = 0.001

init_cash_mean = 8000
init_cash_sd = 1000

init_cash_cat = ["Cash", "Bank account"]
init_cash_cat_prop = [0.4, 0.6]

init_svg_mean = 2000
init_svg_sd = 100

date = datetime.strptime(init_date, "%Y-%m-%d")
cash = norm.rvs(init_cash_mean, init_cash_sd).round(2)

def spend(cat, value):
    global cash, date

    value = min(value, cash)
    cash -= value

    f_date = datetime.strftime(date, input_date_format)

    with open(os.path.join(dirname, "expenses-input.txt"), "a") as file:
        file.write(f"{f_date},{exp_cats[cat]},{value:.2f}\n")


def earn(cat, value):
    global cash, date

    cash += value

    f_date = datetime.strftime(date, input_date_format)

    with open(os.path.join(dirname, "income-input.txt"), "a") as file:
        file.write(f"{f_date},{value:.2f}\n")

# total_value = value of asset gained
def savings(index, total_value, init=False):
    global cash, date, portfolio

    if total_value < 0:
        type = "S"
    elif init:
        type = "I"
    else:
        type = "B"

    total_value = min(total_value, cash)

    unit_value = portfolio[index][1]

    quantity = max(-portfolio[index][2], total_value / unit_value)

    portfolio[index][2] += quantity

    total_value = quantity * unit_value

    if type != "I":
        cash -= total_value

    f_date = datetime.strftime(date, input_date_format)

    with open(os.path.join(dirname, "savings-input.txt"), "a") as file:
        file.write(f"{f_date},{type},{portfolio[index][0]},{abs(quantity)},{unit_value:.2f}\n")


def cash_snapshot():
    global cash, date

    with open(os.path.join(dirname, "cash-input.txt"), "a") as file:
        cash_comp = [init_cash_cat_prop[i] * cash for i, x in enumerate(init_cash_cat)]

        cash_comp[-1] = cash - sum(cash_comp[:-1])

        st = " + ".join([f"{x:.2f} ({init_cash_cat[i]})" for i, x in enumerate(cash_comp)])

        f_date = datetime.strftime(date, input_date_format)

        file.write(f"{f_date}, {st}\n")


with open(os.path.join(dirname, "expenses-input.txt"), "w") as file:
    file.write("date,category,value\n")
with open(os.path.join(dirname, "income-input.txt"), "w") as file:
    file.write("date,value\n")
with open(os.path.join(dirname, "savings-input.txt"), "w") as file:
    file.write("date,type,name,quantity,value\n")
with open(os.path.join(dirname, "cash-input.txt"), "w") as file:
    file.write("date,cash\n")

for i in range(len(portfolio)):
    with open(os.path.join(dirname, f"assets/{portfolio[i][0]}.txt"), "w") as file:
        file.write("date,value\n")

# Initial cash
with open(os.path.join(dirname, "cash-input.txt"), "a") as file:
    cash_snapshot()

# Initial savings
rv = norm.rvs(init_svg_mean, init_svg_sd, size=len(portfolio)).round(2)
for i in range(len(portfolio)):
    total_value = max(0, rv[i])
    savings(i, total_value, init=True)

# Iterates through each day
while date < datetime.strptime(end_date, "%Y-%m-%d"):
    # Updates asset prices
    for asset in portfolio:
        asset[1] += norm.rvs(asset_growth_mean, asset_growth_sd)
        with open(os.path.join(dirname, f"assets/{asset[0]}.txt"), "a") as file:
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
    rv_n = norm.rvs(exp_mean, exp_sd, size=len(exp_cats)).round(2)
    for i in range(len(exp_cats)):
        if rv_u[i] < exp_days[i] / 365:
            value = max(0, rv_n[i])
            spend(i, value)

    # Buying and selling savings
    rv_u = uniform.rvs(size=len(portfolio))
    rv_n = norm.rvs(svg_mean, svg_sd, size=len(portfolio)).round(2)
    for i in range(len(portfolio)):
        if rv_u[i] < svg_days / 365:
            savings(i, rv_n[i])

    date = date + timedelta(days=1)
