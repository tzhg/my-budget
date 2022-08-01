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
prl_df = pd.read_csv(os.path.join(dirname, f"./{data_dir}/profit-loss-input.txt"))

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
prl_df["date"] = pd.to_datetime(prl_df["date"], format=input_date_format)

for _, df in ass_df.items():
    df["date"] = pd.to_datetime(df["date"], format=input_date_format)

start_date = csh_df["date"].iat[0]

# Adds month column
exp_df["month"] = (exp_df["date"].dt.year - start_date.year) * 12 + exp_df["date"].dt.month - start_date.month
inc_df["month"] = (inc_df["date"].dt.year - start_date.year) * 12 + inc_df["date"].dt.month - start_date.month
svg_df["month"] = (svg_df["date"].dt.year - start_date.year) * 12 + svg_df["date"].dt.month - start_date.month
prl_df["month"] = (prl_df["date"].dt.year - start_date.year) * 12 + prl_df["date"].dt.month - start_date.month

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
prl2_df = prl_df.copy()

exp2_df = exp2_df.drop("category", axis=1)
svg2_df = svg2_df.drop(["type", "name", "quantity", "value"], axis=1)
prl2_df = prl2_df.drop("name", axis=1)

svg2_df = svg2_df.rename(columns={"total_value": "value"})

svg2B_df = svg2_df[svg_df["type"] == "B"]
svg2S_df = svg2_df[svg_df["type"] == "S"]

exp2_df["value"] *= -1
svg2B_df["value"] *= -1

cfl_df = pd.concat([exp2_df, inc_df, svg2B_df, svg2S_df, prl2_df])
cfl_df["month"] = (cfl_df["date"].dt.year - start_date.year) * 12 + cfl_df["date"].dt.month - start_date.month

# Sorts by date
cfl_df = cfl_df.sort_values(by=["date"])
cfl_df = cfl_df.reset_index()

no_months = cfl_df["month"].iat[-1] + 1

eo_list = []
cash_list = []

cash_counter = csh_df.at[0, "total_cash"]
snap_idx = 1
month_idx = 0

for i, row in cfl_df.iterrows():
    if snap_idx < len(csh_df):
        # Finishes snapshot
        if row["date"] >= csh_df.at[snap_idx, "date"]:
            # Calculates errors/omissions
            eo = csh_df.at[snap_idx, "total_cash"] - cash_counter

            eo_list.append([csh_df.at[snap_idx, "date"], eo])

            if abs(eo) >= 0.005:
                date_str = datetime.strftime(csh_df.at[snap_idx, "date"], input_date_format)
                print(f"{date_str} cash snapshot: {eo:.2f}")

            # Prepares next snapshot
            cash_counter = csh_df.at[snap_idx, "total_cash"]
            snap_idx += 1

    # Finishes month
    if row["month"] > month_idx:
        while row["month"] > month_idx:
            cash_list.append(cash_counter)
            month_idx += 1

    cash_counter += row["value"]

# Adds final month
while no_months > month_idx:
    cash_list.append(cash_counter)
    month_idx += 1

# Finishes snapshot on final day
if snap_idx < len(csh_df):
    eo = csh_df.at[snap_idx, "total_cash"] - cash_counter

    eo_list.append([csh_df.at[snap_idx, "date"], eo])

    if abs(eo) >= 0.005:
        date_str = datetime.strftime(csh_df.at[snap_idx, "date"], input_date_format)
        print(f"{date_str} cash snapshot: {eo:.2f}")

inc_eo_list = [x for x in eo_list if x[1] > 0]
inc_df = pd.concat(
    [inc_df, pd.DataFrame(inc_eo_list, columns=["date", "value"])],
    ignore_index=True)

exp_eo_list = [[x[0], "Other", -x[1]] for x in eo_list if x[1] < 0]
exp_df = pd.concat(
    [exp_df, pd.DataFrame(exp_eo_list, columns=["date", "category", "value"])],
    ignore_index=True)

exp_df["month"] = (exp_df["date"].dt.year - start_date.year) * 12 + exp_df["date"].dt.month - start_date.month
inc_df["month"] = (inc_df["date"].dt.year - start_date.year) * 12 + inc_df["date"].dt.month - start_date.month

# ============================================================================ #
# Savings

month_idx = 0

portfolio = []

savings_list = []
debt_list = []
prl_list = []

for i, row in svg_df.iterrows():
    # Finishes month
    if row["month"] > month_idx:
        while row["month"] > month_idx:
            pf_value = [
                float(ass_df[ass[1]][ass_df[ass[1]]["date"] <= ass[0]].iloc[-1]["value"] * ass[2])
                if ass[1] in ass_df
                else float(ass[3] * ass[2])
                for ass in portfolio]
            savings_list.append(sum([max(val, 0) for val in pf_value]))
            debt_list.append(sum([-min(val, 0) for val in pf_value]))

            month_idx += 1

    if row["type"] == "I" or row["type"] == "B":
        portfolio.append([row["date"], row["name"], row["quantity"], row["value"]])
    elif row["type"] == "S":
        q_to_sell = row["quantity"]
        j = 0
        while q_to_sell > 0 and j < len(portfolio) and portfolio[j][0] <= row["date"]:
            if portfolio[j][1] == row["name"]:
                min_quant = min(portfolio[j][2], q_to_sell)

                portfolio[j][2] -= min_quant
                q_to_sell -= min_quant

                buy_value = portfolio[j][3] * min_quant
                sell_value = row["value"] * min_quant

                prl_list.append([row["date"], row["name"], sell_value - buy_value])

            j += 1

# Adds final month
while no_months > month_idx:
    pf_value = [
        float(ass_df[ass[1]][ass_df[ass[1]]["date"] <= ass[0]].iloc[-1]["value"] * ass[2])
        if ass[1] in ass_df
        else float(ass[3] * ass[2])
        for ass in portfolio]
    savings_list.append(sum([max(val, 0) for val in pf_value]))
    debt_list.append(sum([-min(val, 0) for val in pf_value]))

    month_idx += 1

prof_list = [x for x in prl_list if x[2] > 0]
prof_df = pd.concat(
    [prl_df[prl_df["value"] > 0], pd.DataFrame(prof_list, columns=["date", "name", "value"])],
    ignore_index=True)

loss_list = [x for x in prl_list if x[2] < 0]
loss_df = pd.concat(
    [prl_df[prl_df["value"] < 0], pd.DataFrame(loss_list, columns=["date", "name", "value"])],
    ignore_index=True)

loss_df["value"] *= -1

prof_df["month"] = (prof_df["date"].dt.year - start_date.year) * 12 + prof_df["date"].dt.month - start_date.month
loss_df["month"] = (loss_df["date"].dt.year - start_date.year) * 12 + loss_df["date"].dt.month - start_date.month

# ============================================================================ #
# Income and expenses

# Aggregates entries by month and category
exp_df = exp_df.groupby(["month", "category"]).sum()
inc_df = inc_df.groupby("month").sum()
prof_df = prof_df.groupby("month").sum()
loss_df = loss_df.groupby("month").sum()

# Reshapes df to show categories as columns
exp_df = exp_df.unstack("category", fill_value=0)

# Ensures every month is present
exp_df = exp_df.reindex(range(no_months), fill_value=0)
inc_df = inc_df.reindex(range(no_months), fill_value=0)
prof_df = prof_df.reindex(range(no_months), fill_value=0)
loss_df = loss_df.reindex(range(no_months), fill_value=0)

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
    debt_list,
    inc_df["value"].to_list(),
    exp_df["total"].to_list(),
    prof_df["value"].to_list(),
    loss_df["value"].to_list(),
    exp_df["value", "Housing"].to_list(),
    exp_df["value", "Food"].to_list(),
    exp_df["value", "Shopping"].to_list(),
    exp_df["value", "Utilities"].to_list(),
    exp_df["value", "Health"].to_list(),
    exp_df["value", "Leisure"].to_list()]

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
