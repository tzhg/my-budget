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
exp_days = [2, 100, 10, 15, 10, 10, 15]
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
exp_monthly = [1800, 0, 300, 0, 0, 0, 0]
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

asset_growth_mean = 0.0005
asset_growth_sd = 0.01

init_cash_mean = 7000
init_cash_sd = 1000

init_cash_cat = ["Cash", "Bank account"]
init_cash_cat_prop = [0.4, 0.6]

init_svg_mean = 0
init_svg_sd = 1

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
def savings(index, type, total_value):
    global cash, date, portfolio

    if type == "S":
        total_value *= -1

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
    savings(i, "I", total_value)

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
    mu = exp_mean + cash * exp_multi[i] / 1000
    rv_n = norm.rvs(mu, exp_sd, size=len(exp_cats)).round(2)
    for i in range(len(exp_cats)):
        if rv_u[i] < exp_days[i] / 365:
            value = max(0, rv_n[i])
            spend(i, value)

    # Buying savings
    rv_u = uniform.rvs(size=len(portfolio))
    mu = svgb_mean + cash * svgb_multi / 1000
    rv_n = norm.rvs(mu, svgb_sd, size=len(portfolio)).round(2)
    for i in range(len(portfolio)):
        if rv_u[i] < svgb_days / 365:
            value = max(0, rv_n[i])
            savings(i, "B", value)

    # Selling savings
    rv_u = uniform.rvs(size=len(portfolio))
    mu = svgs_mean + cash * svgs_multi / 1000
    rv_n = norm.rvs(mu, svgs_sd, size=len(portfolio)).round(2)
    for i in range(len(portfolio)):
        if rv_u[i] < svgs_days / 365:
            value = max(0, rv_n[i])
            savings(i, "S", value)

    date = date + timedelta(days=1)
