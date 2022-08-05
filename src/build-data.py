#!/bin/bash

import os, json
from datetime import datetime
import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None

input_date_format = "%d/%m/%Y"

# Directory of input data
#data_dir = "data-simulated"
data_dir = "data-simulated"

# Current directory
dirname = os.path.dirname(os.path.abspath(__file__))

exp_df = pd.read_csv(os.path.join(dirname, f"./{data_dir}/expenses-input.csv"))
inc_df = pd.read_csv(os.path.join(dirname, f"./{data_dir}/income-input.csv"))
csh_df = pd.read_csv(os.path.join(dirname, f"./{data_dir}/cash-input.csv"))
svg_df = pd.read_csv(os.path.join(dirname, f"./{data_dir}/savings-input.csv"))
prl_df = pd.read_csv(os.path.join(dirname, f"./{data_dir}/profit-loss-input.csv"))
sin_df = pd.read_csv(os.path.join(dirname, f"./{data_dir}/savings-info.csv"))

asset_dir = os.path.join(dirname, f"./{data_dir}/assets")

assets_list = [
    os.path.splitext(os.fsdecode(file))[0]
    for file in os.listdir(asset_dir)]

ass_df = {
    name: pd.read_csv(os.path.join(dirname, f"./{data_dir}/assets/{name}.csv"))
    for name in assets_list}

# Set datetime type
exp_df["date"] = pd.to_datetime(exp_df["date"], format=input_date_format)
inc_df["date"] = pd.to_datetime(inc_df["date"], format=input_date_format)
csh_df["date"] = pd.to_datetime(csh_df["date"], format=input_date_format)
svg_df["date"] = pd.to_datetime(svg_df["date"], format=input_date_format)
prl_df["date"] = pd.to_datetime(prl_df["date"], format=input_date_format)

for _, df in ass_df.items():
    df["date"] = pd.to_datetime(df["date"], format=input_date_format)

start_date_dt = csh_df["date"].iat[0]
start_date = [start_date_dt.day, start_date_dt.month, start_date_dt.year]

# Adds month column
exp_df["month"] = (exp_df["date"].dt.year - start_date[2]) * 12 + exp_df["date"].dt.month - start_date[1]
inc_df["month"] = (inc_df["date"].dt.year - start_date[2]) * 12 + inc_df["date"].dt.month - start_date[1]
svg_df["month"] = (svg_df["date"].dt.year - start_date[2]) * 12 + svg_df["date"].dt.month - start_date[1]
prl_df["month"] = (prl_df["date"].dt.year - start_date[2]) * 12 + prl_df["date"].dt.month - start_date[1]

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
cfl_df["month"] = (cfl_df["date"].dt.year - start_date[2]) * 12 + cfl_df["date"].dt.month - start_date[1]

# Sorts by date
cfl_df = cfl_df.sort_values(by=["date"])
cfl_df = cfl_df.reset_index()

csh_df = csh_df.sort_values(by=["date"])
csh_df = csh_df.reset_index()

end_date_dt = max(cfl_df["date"].iat[-1], csh_df["date"].iat[-1])
end_date = [end_date_dt.day, end_date_dt.month, end_date_dt.year]

no_months = (end_date[2] - start_date[2]) * 12 + end_date[1] - start_date[1] + 1

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

exp_df["month"] = (exp_df["date"].dt.year - start_date[2]) * 12 + exp_df["date"].dt.month - start_date[1]
inc_df["month"] = (inc_df["date"].dt.year - start_date[2]) * 12 + inc_df["date"].dt.month - start_date[1]

# ============================================================================ #
# Savings

month_idx = 0

portfolio = []

# Types of savings
financial_list = []
real_list = []
debt_list = []

# Profits and losses
prl_list = []

svg_df = pd.merge(svg_df, sin_df, how="left", on="name")

for i, row in svg_df.iterrows():
    # Finishes month
    if row["month"] > month_idx:
        while row["month"] > month_idx:
            pf_value = [
                [
                    float(ass_df[n][ass_df[n]["date"] <= d].iloc[-1]["value"] * q),
                    c]
                if n in ass_df
                else [float(v * q), c]
                for d, n, q, v, c in portfolio]

            financial_list.append(sum([val for val, cat in pf_value if cat == "financial"]))
            real_list.append(sum([val for val, cat in pf_value if cat == "real"]))
            debt_list.append(sum([-val for val, cat in pf_value if cat == "debt"]))

            month_idx += 1

    if row["type"] == "I" or row["type"] == "B":
        portfolio.append([row["date"], row["name"], row["quantity"], row["value"], row["category"]])
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
        [float(ass_df[n][ass_df[n]["date"] <= d].iloc[-1]["value"] * q),
            c]
        if n in ass_df
        else [float(v * q), c]
        for d, n, q, v, c in portfolio]

    financial_list.append(sum([val for val, cat in pf_value if cat == "financial"]))
    real_list.append(sum([val for val, cat in pf_value if cat == "real"]))
    debt_list.append(sum([-val for val, cat in pf_value if cat == "debt"]))

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

if not prof_df.empty:
    prof_df["month"] = (prof_df["date"].dt.year - start_date[2]) * 12 + prof_df["date"].dt.month - start_date[1]
if not loss_df.empty:
    loss_df["month"] = (loss_df["date"].dt.year - start_date[2]) * 12 + loss_df["date"].dt.month - start_date[1]

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

with open(os.path.join(dirname, f"./{data_dir}/viz-config.json"), "r") as file:
    viz_config = json.load(file)

info = {
    "startDate": start_date,
    "endDate": end_date
}

income_list = inc_df["value"].to_list()
expenses_list = exp_df["total"].to_list()
profit_list = prof_df["value"].to_list()
loss_list = loss_df["value"].to_list()

net_assets = [
    cash_list[i] + financial_list[i] + real_list[i] - debt_list[i]
    for i in range(no_months)];

net_income = [
    income_list[i] + profit_list[i] - expenses_list[i] - loss_list[i]
    for i in range(no_months)];

monthlyData = {
    "cash": cash_list,
    "financial": financial_list,
    "real": real_list,
    "debt": debt_list,
    "netAssets": net_assets,
    "income": income_list,
    "expenses": expenses_list,
    "profit": profit_list,
    "loss": loss_list,
    "netIncome": net_income,
    "housing": exp_df["value", "Housing"].to_list(),
    "food": exp_df["value", "Food"].to_list(),
    "shopping": exp_df["value", "Shopping"].to_list(),
    "utilities": exp_df["value", "Utilities"].to_list(),
    "health": exp_df["value", "Health"].to_list(),
    "leisure": exp_df["value", "Leisure"].to_list()}

# [Current month, yearly average, historical months] for each variable
data = {
    key: [[val[-1]], [np.mean(val[-13:-1])], val[-2::-1]]
    for (key, val) in monthlyData.items()}

output = {
    "config": viz_config,
    "info": info,
    "data": data}

# Data as a JSON string
data_json = json.dumps(output, indent=4)

# Saves data_json in current directory
with open(os.path.join(dirname, "./data.json"), "w") as file:
    file.write(data_json)
