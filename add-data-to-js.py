#!/bin/bash

import os, json, math, itertools
from datetime import datetime, timedelta
from itertools import accumulate
import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None

input_date_format = "%d/%m/%Y"

# Current directory
dirname = os.path.dirname(os.path.abspath(__file__))

data_dir = "data-simulated"
#data_dir = "data"

exp_df = pd.read_csv(os.path.join(dirname, f"./{data_dir}/expenses-input.txt"))
inc_df = pd.read_csv(os.path.join(dirname, f"./{data_dir}/income-input.txt"))
csh_df = pd.read_csv(os.path.join(dirname, f"./{data_dir}/cash-input.txt"))
svg_df = pd.read_csv(os.path.join(dirname, f"./{data_dir}/savings-input.txt"))

asset_dir = os.path.join(dirname, f"./{data_dir}/assets")

assets_list = [
    os.path.splitext(os.fsdecode(file))[0]
    for file in os.listdir(asset_dir)]

ass_df = {
    name: pd.read_csv(os.path.join(dirname, f"./{data_dir}/assets/{name}.txt"))
    for name in assets_list}

# Set datetime type
exp_df["date"] = pd.to_datetime(exp_df["date"], format=input_date_format)
inc_df["date"] = pd.to_datetime(inc_df["date"], format=input_date_format)
csh_df["date"] = pd.to_datetime(csh_df["date"], format=input_date_format)
svg_df["date"] = pd.to_datetime(svg_df["date"], format=input_date_format)

for _, df in ass_df.items():
    df["date"] = pd.to_datetime(df["date"], format=input_date_format)

start_date = csh_df["date"].iat[0]

# Adds month column
exp_df["month"] = (exp_df["date"].dt.year - start_date.year) * 12 + exp_df["date"].dt.month - start_date.month
inc_df["month"] = (inc_df["date"].dt.year - start_date.year) * 12 + inc_df["date"].dt.month - start_date.month
svg_df["month"] = (svg_df["date"].dt.year - start_date.year) * 12 + svg_df["date"].dt.month - start_date.month

# ============================================================================ #
# Cash

def total_cash(x):
    if type(x) == int:
        return x
    return sum([float(s.split("(")[0]) for s in x.split("+")])


csh_df["total_cash"] = csh_df.cash.apply(total_cash)
svg_df["total_value"] = svg_df["quantity"] * svg_df["value"]

exp2_df = exp_df.copy()
svg2_df = svg_df.copy()

exp2_df = exp2_df.drop("category", axis=1)
svg2_df = svg2_df.drop(["type", "name", "quantity", "value"], axis=1)

svg2_df = svg2_df.rename(columns={"total_value": "value"})

svg2B_df = svg2_df[svg_df["type"] == "B"]
svg2S_df = svg2_df[svg_df["type"] == "S"]

exp2_df["value"] *= -1
svg2B_df["value"] *= -1

cfl_df = pd.concat([exp2_df, inc_df, svg2B_df, svg2S_df])
cfl_df["month"] = (cfl_df["date"].dt.year - start_date.year) * 12 + cfl_df["date"].dt.month - start_date.month

# Sorts by date
cfl_df = cfl_df.sort_values(by=["date"])
cfl_df = cfl_df.reset_index()

no_months = cfl_df["month"].iat[-1] + 1

eo_list = []
cash_list = []

cash_counter = csh_df.at[0, "total_cash"]
snapIdx = 1
monthIdx = 0

for i, row in cfl_df.iterrows():
    if snapIdx < len(csh_df):
        # Finishes snapshot
        if row["date"] >= csh_df.at[snapIdx, "date"]:
            # Calculates errors/omissions
            eo = csh_df.at[snapIdx, "total_cash"] - cash_counter

            eo_list.append([csh_df.at[snapIdx, "date"], eo])

            if abs(eo) >= 0.005:
                date_str = datetime.strftime(csh_df.at[snapIdx, "date"], input_date_format)
                print(f"{date_str} cash snapshot: {eo:.2f}")

            # Prepares next snapshot
            cash_counter = csh_df.at[snapIdx, "total_cash"]
            snapIdx += 1

    # Finishes month
    if row["month"] > monthIdx:
        while row["month"] > monthIdx:
            cash_list.append(cash_counter)
            monthIdx += 1

    cash_counter += row["value"]

# Adds final month
while no_months > monthIdx:
    cash_list.append(cash_counter)
    monthIdx += 1

# Finishes snapshot on final day
if snapIdx < len(csh_df):
    eo = csh_df.at[snapIdx, "total_cash"] - cash_counter

    eo_list.append([csh_df.at[snapIdx, "date"], eo])

    if abs(eo) >= 0.005:
        date_str = datetime.strftime(csh_df.at[snapIdx, "date"], input_date_format)
        print(f"{date_str} cash snapshot: {eo:.2f}")

exp_eo_list = [[x[0], "Other", -x[1]] for x in eo_list if x[1] < 0]
exp_df = pd.concat(
    [exp_df, pd.DataFrame(exp_eo_list, columns=["date", "category", "value"])],
    ignore_index=True)

inc_eo_list = [x for x in eo_list if x[1] < 0]
inc_df = pd.concat(
    [inc_df, pd.DataFrame(inc_eo_list, columns=["date", "value"])],
    ignore_index=True)

# ============================================================================ #
# Savings

# Gets last available price of an asset
def asset_price(date, name, quantity):
    value = ass_df[name][ass_df[name]["date"] <= date].iloc[-1]["value"]
    return float(value * quantity)


monthIdx = 0
profit = 0
loss = 0

portfolio = []

savings_list = []
profit_list = []
loss_list = []

for i, row in svg_df.iterrows():
    # Finishes month
    if row["month"] > monthIdx:
        while row["month"] > monthIdx:
            pf_value = sum([asset_price(*x) for x in portfolio])
            savings_list.append(pf_value)
            profit_list.append(profit)
            loss_list.append(loss)
            profit = 0
            loss = 0

            monthIdx += 1

    if row["type"] == "I" or row["type"] == "B":
        portfolio.append([row["date"], row["name"], row["quantity"]])
    elif row["type"] == "S":
        q_to_sell = row["quantity"]
        j = 0
        while q_to_sell > 0 and j < len(portfolio) and portfolio[j][0] <= row["date"]:
            if portfolio[j][1] == row["name"]:
                min_quant = min(portfolio[j][2], q_to_sell)

                portfolio[j][2] -= min_quant
                q_to_sell -= min_quant

                buy_value = asset_price(portfolio[j][0], portfolio[j][1], min_quant)
                sell_value = asset_price(row["date"], row["name"], min_quant)

                if sell_value > buy_value:
                    profit += sell_value - buy_value
                else:
                    loss +=  buy_value - sell_value

            j += 1

# Adds final month
while no_months > monthIdx:
    pf_value = sum([asset_price(*x) for x in portfolio])
    savings_list.append(pf_value)
    profit_list.append(profit)
    loss_list.append(loss)
    profit = 0
    loss = 0
    monthIdx += 1

print(profit_list)
print(loss_list)

# ============================================================================ #
# Income and expenses

# Aggregates entries by month and category
exp_df = exp_df.groupby(["month", "category"]).sum()
inc_df = inc_df.groupby("month").sum()

# Reshapes df to show categories as columns
exp_df = exp_df.unstack("category", fill_value=0)

# Ensures every month is present
exp_df = exp_df.reindex(range(no_months), fill_value=0)
inc_df = inc_df.reindex(range(no_months), fill_value=0)

exp_df["total"] = exp_df.sum(axis=1)

with open(os.path.join(dirname, f"./{data_dir}/viz-parameters.json"), "r") as file:
    viz_para = json.load(file)

info = {
    "startMonth": start_date.month - 1,
    "startYear": start_date.year
}

monthlyData = [
    cash_list,
    savings_list,
    exp_df["total"].to_list(),
    inc_df["value"].to_list(),
    exp_df["value", "Housing"].to_list(),
    exp_df["value", "Food"].to_list(),
    exp_df["value", "Shopping"].to_list(),
    exp_df["value", "Utilities"].to_list(),
    exp_df["value", "Health"].to_list(),
    exp_df["value", "Leisure"].to_list(),
    profit_list,
    loss_list]

# [Current month, yearly average, historical months] for each variable
data = [
    [[lst[-1]], [np.mean(lst[-13:-1])], lst[-2::-1]]
    for lst in monthlyData]

# Separates pl_list into profit list and loss list
#profit_list = [[max(0, val) for val in lst] for lst in data[10]]
#loss_list = [[abs(min(0, val)) for val in lst] for lst in data[10]]

#data = data[:10] + [profit_list, loss_list]

output = {
    "para": viz_para,
    "info": info,
    "data": data}

# Data as a JSON string
data_json = json.dumps(output, indent=4)

# Wraps JSON string in JavaScript module syntax, and saves it to ../js
with open(os.path.join(dirname, "./js/importData.js"), "w") as file:
    file.write(f"export function importData() {{\n	return {data_json};\n}}")
