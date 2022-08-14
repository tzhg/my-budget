#!/bin/bash

import os, json
from datetime import datetime
import pandas as pd
import numpy as np

pd.options.mode.chained_assignment = None
pd.set_option("display.max_rows", None)

input_date_format = "%d/%m/%Y"

# Directory of input data
data_dir = "data-simulated"
#data_dir = "data"

# Current directory
dirname = os.path.dirname(os.path.abspath(__file__))

# Information about type values in cash flow data
types = {
    "expenses": {
        "name": "Expenses",
        "categories": {
            "housing": {
                "name": "Housing"},
            "food": {
                "name": "Food"},
            "shopping": {
                "name": "Shopping"},
            "utilities": {
                "name": "Utilities"},
            "health": {
                "name": "Health"},
            "leisure": {
                "name": "Leisure"},
            "other": {
                "name": "Other"}},
        "factor": -1,
        "reference": False},
    "expenses_neg": {
        "name": "Expense negation",
        "categories": {
            "financial": {
                "name": "Sale"},
            "real": {
                "name": "Reimbursement"}},
        "factor": 1,
        "reference": True},
    "income": {
        "name": "Income",
        "categories": {
            "default": {
                "name": ""}},
        "factor": 1,
        "reference": False},
    "savings_buy": {
        "name": "Savings buying",
        "base": "savings",
        "categories": {
            "financial": {
                "name": "Financial"},
            "real": {
                "name": "Real"}},
        "factor": -1,
        "reference": False},
    "savings_sell": {
        "name": "Savings selling",
        "base": "savings",
        "categories": {
            "default": {
                "name": ""}},
        "factor": 1,
        "reference": True},
    "debt_buy": {
        "name": "Debt buying",
        "base": "debt",
        "categories": {
            "default": {
                "name": ""}},
        "factor": 1,
        "reference": False},
    "debt_sell": {
        "name": "Debt selling",
        "base": "debt",
        "categories": {
            "default": {
                "name": ""}},
        "factor": -1,
        "reference": True},
    "asset_income": {
        "name": "Asset income",
        "categories": {
            "default": {
                "name": ""}},
        "factor": 1,
        "reference": True},
    "asset_expenses": {
        "name": "Asset expenses",
        "categories": {
            "default": {
                "name": ""}},
        "factor": -1,
        "reference": True}}

monthly_data = {}


# ============================================================================ #
# Input data


# Number of months between start date and datetime object d
def num_months(d):
    return (d.year - start_date.year) * 12 + d.month - start_date.month


# Calculates total cash from multiple sources
def total_cash(cash_array):
    return sum([obj["value"] for obj in cash_array])


# Loads initial assets data

with open(os.path.join(dirname, f"./{data_dir}/init-assets.json"), "r") as file:
    init_assets = json.load(file)

start_date = datetime.strptime(init_assets["date"], input_date_format)

# Replaces type and category names with standard form
for asset in init_assets["savings"]:
    for cat, obj in types["savings_buy"]["categories"].items():
        asset["category"] = asset["category"].replace(obj["name"], cat)

# Loads cash snapshot data

with open(os.path.join(dirname, f"./{data_dir}/cash-snapshots.json"), "r") as file:
    cash_snapshots = json.load(file)

for i in range(len(cash_snapshots)):
    cash_snapshots[i]["date"] = datetime.strptime(cash_snapshots[i]["date"], input_date_format)
    cash_snapshots[i]["cash"] = total_cash(cash_snapshots[i]["cash"])

cash_snapshots = sorted(cash_snapshots, key=lambda d: d["date"])

# Loads cash flow data

cash_flow_df = pd.read_csv(os.path.join(dirname, f"./{data_dir}/cash-flow.csv"))
cash_flow_df["date"] = pd.to_datetime(cash_flow_df["date"], format=input_date_format)

cash_flow_df = cash_flow_df.sort_values(by=["date"])
cash_flow_df = cash_flow_df.set_index("id")

cash_flow_df["category"].fillna("default", inplace=True)

# Replaces type and category names with standard form
for type, obj in types.items():
    cash_flow_df["type"].replace(to_replace={obj["name"]: type}, inplace=True)
    cash_flow_df["category"].replace(to_replace={obj2["name"]: cat for cat, obj2 in obj["categories"].items()}, inplace=True)

# Ensures every type and category are present
null_rows = [[
        [start_date, type, cat, 0, 0]
        for cat, obj2 in obj["categories"].items()]
    for type, obj in types.items()]
null_df = pd.DataFrame(
    [x for y in null_rows for x in y],
    columns=["date", "type", "category", "quantity", "value"])
cash_flow_df = pd.concat([cash_flow_df, null_df], ignore_index=True)

cash_flow_df["month"] = num_months(cash_flow_df["date"].dt)
cash_flow_df["total_value"] = cash_flow_df["quantity"] * cash_flow_df["value"]
end_date = max(cash_snapshots[-1]["date"], cash_flow_df["date"].iat[-1])
no_months = num_months(end_date) + 1

# Validation...
#cash_flow_df["type"].isin(some_list_of_values)

# Loads asset value data

asset_values_df = {}
for file in os.listdir(os.path.join(dirname, f"./{data_dir}/asset-values")):
    id = os.path.splitext(os.fsdecode(file))[0]
    df = pd.read_csv(os.path.join(dirname, f"./{data_dir}/asset-values/{id}.csv"))

    df["date"] = pd.to_datetime(df["date"], format=input_date_format)
    df["month"] = num_months(df["date"].dt)

    asset_values_df[id] = df


# ============================================================================ #
# Assets


eo_list = []
cg_list = []

monthly_data["cash"] = []
monthly_data["financial"] = []
monthly_data["real"] = []
monthly_data["debt"] = []

snap_idx = 0
month_idx = 0

cash_counter = total_cash(init_assets["cash"])
portfolio = {
    "savings": init_assets["savings"],
    "debt": init_assets["debt"]}


# Adds initial assets to cash flow list to ensure they can be referenced

savings_init_df = pd.DataFrame(
    [
        [obj["id"], start_date, "savings_buy", obj["category"], 0, 0, 0, 0]
        for obj in init_assets["savings"]],
    columns=["id", "date", "type", "category", "quantity", "value", "month", "total_value"])
savings_init_df = savings_init_df.set_index("id")
cash_flow_df = pd.concat([cash_flow_df, savings_init_df])

debt_init_df = pd.DataFrame(
    [
        [obj["id"], start_date, "debt_buy", 0, 0, 0, 0]
        for obj in init_assets["debt"]],
    columns=["id", "date", "type", "quantity", "value", "month", "total_value"])
debt_init_df = debt_init_df.set_index("id")
cash_flow_df = pd.concat([cash_flow_df, debt_init_df])

for i, row in cash_flow_df.iterrows():
    # Finishes snapshot
    if snap_idx < len(cash_snapshots):
        snapshot = cash_snapshots[snap_idx]
        if row["date"] >= snapshot["date"]:
            # Calculates errors/omissions
            eo = snapshot["cash"] - cash_counter

            eo_list.append([snapshot["date"], eo])

            if abs(eo) >= 0.005:
                date_str = datetime.strftime(snapshot["date"], input_date_format)
                print(f"{date_str} cash snapshot: {eo:.2f}")

            # Prepares next snapshot
            cash_counter = snapshot["cash"]
            snap_idx += 1

    # Finishes month
    if row["month"] > month_idx:
        while row["month"] > month_idx:
            monthly_data["cash"].append(cash_counter)

            financial_count = 0
            real_count = 0
            debt_count = 0

            for obj in portfolio["savings"]:
                if obj["id"] in asset_values_df:
                    curr_value = asset_values_df[obj["id"]][asset_values_df[obj["id"]]["month"] <= month_idx].iloc[-1]["value"]
                else:
                    curr_value = obj["value"]
                curr_tvalue = float(curr_value) * obj["quantity"]

                if obj["category"] == "financial":
                    financial_count += curr_tvalue
                elif obj["category"] == "real":
                    real_count += curr_tvalue

            for obj in portfolio["debt"]:
                if obj["id"] in asset_values_df:
                    curr_value = asset_values_df[obj["id"]][asset_values_df[obj["id"]]["month"] <= month_idx].iloc[-1]["value"]
                else:
                    curr_value = obj["value"]
                curr_tvalue = float(curr_value) * obj["quantity"]

                debt_count += curr_tvalue

            monthly_data["financial"].append(financial_count)
            monthly_data["real"].append(real_count)
            monthly_data["debt"].append(debt_count)

            month_idx += 1

    row["total_value"] *= types[row["type"]]["factor"]
    row["value"] *= types[row["type"]]["factor"]

    # Updates cash
    cash_counter += row["total_value"]

    if row["type"] == "savings_buy" or row["type"] == "debt_buy":
        if not pd.isnull(row["reference"]):
            id = row["reference"]
            cat = cash_flow_df.at[row["reference"], "category"]
        else:
            id = i
            cat = row["category"]
        portfolio[types[row["type"]]["base"]].append({
            "id": id,
            "category": cat,
            "quantity": row["quantity"],
            "value": row["value"]})
    elif row["type"] == "savings_sell" or row["type"] == "debt_sell":
        q_to_sell = row["quantity"]
        # Insert validation here
        for asset in portfolio[types[row["type"]]["base"]]:
            if asset["id"] == row["reference"]:
                min_quant = min(asset["quantity"], q_to_sell)

                asset["quantity"] -= min_quant
                q_to_sell -= min_quant

                buy_value = asset["value"] * min_quant
                sell_value = row["value"] * min_quant

                cg_list.append([row["date"], row["reference"], sell_value - buy_value])

                if q_to_sell == 0:
                    break

# Adds final month
while no_months > month_idx:
    monthly_data["cash"].append(cash_counter)

    financial_count = 0
    real_count = 0
    debt_count = 0

    for obj in portfolio["savings"]:
        if obj["id"] in asset_values_df:
            curr_value = asset_values_df[obj["id"]][asset_values_df[obj["id"]]["month"] <= month_idx].iloc[-1]["value"]
        else:
            curr_value = obj["value"]
        curr_tvalue = float(curr_value) * obj["quantity"]

        if obj["category"] == "financial":
            financial_count += curr_tvalue
        elif obj["category"] == "real":
            real_count += curr_tvalue

    for obj in portfolio["debt"]:
        if obj["id"] in asset_values_df:
            curr_value = asset_values_df[obj["id"]][asset_values_df[obj["id"]]["month"] <= month_idx].iloc[-1]["value"]
        else:
            curr_value = obj["value"]
        curr_tvalue = float(curr_value) * obj["quantity"]

        debt_count += curr_tvalue

    monthly_data["financial"].append(financial_count)
    monthly_data["real"].append(real_count)
    monthly_data["debt"].append(debt_count)

    month_idx += 1

# Finishes snapshot on final day
if snap_idx < len(cash_snapshots):
    snapshot = cash_snapshots[snap_idx]
    eo = snapshot["cash"] - cash_counter

    eo_list.append([snapshot["date"], eo])

    if abs(eo) >= 0.005:
        date_str = datetime.strftime(snapshot["date"], input_date_format)
        print(f"{date_str} cash snapshot: {eo:.2f}")

# Dataframe of errors/omissions
eo_df = pd.DataFrame(
    [
        [x[0], "income", "default", 1, x[1]]
        if x[1] > 0
        else
        [x[0], "expenses", "other", 1, -x[1]]
        for x in eo_list],
    columns=["date", "type", "category", "quantity", "value"])

eo_df["month"] = num_months(eo_df["date"].dt)
eo_df["total_value"] = eo_df["quantity"] * eo_df["value"]

# Adds errors/omissions to cash flow dataframe
cash_flow_df = pd.concat([cash_flow_df, eo_df], ignore_index=True)

# Dataframe of capital gains/losses
cg_df = pd.DataFrame(
    [
        [x[0], "asset_income", "default", 1, x[2], x[1]]
        if x[2] > 0
        else
        [x[0], "asset_expenses", "default", 1, -x[2], x[1]]
        for i, x in enumerate(cg_list)],
    columns=["date", "type", "category", "quantity", "value", "reference"])

cg_df["month"] = num_months(cg_df["date"].dt)
cg_df["total_value"] = cg_df["quantity"] * cg_df["value"]

# Adds capital gains/losses to cash flow dataframe
cash_flow_df = pd.concat([cash_flow_df, cg_df], ignore_index=True)


# ============================================================================ #
# Income and expenses


# Aggregates entries by month and category

cash_flow_df = cash_flow_df.groupby(["month", "type", "category"]).sum()

# Reshapes df to show categories as columns
cash_flow_df = cash_flow_df.unstack(["type", "category"], fill_value=0)

monthly_data["income"] = cash_flow_df.loc[:, ("total_value", "income", "default")].to_list()
monthly_data["expenses"] = cash_flow_df.loc[:, ("total_value", "expenses", slice(None))].sum(axis=1).to_list()
monthly_data["profit"] = cash_flow_df.loc[:, ("total_value", "asset_income", "default")].to_list()
monthly_data["loss"] = cash_flow_df.loc[:, ("total_value", "asset_expenses", "default")].to_list()

monthly_data["netAssets"] = [
    monthly_data["cash"][i] + monthly_data["financial"][i] + monthly_data["real"][i] - monthly_data["debt"][i]
    for i in range(no_months)];

monthly_data["netIncome"] = [
    monthly_data["income"][i] + monthly_data["profit"][i] - monthly_data["expenses"][i] - monthly_data["loss"][i]
    for i in range(no_months)];

monthly_data["housing"] = cash_flow_df.loc[:, ("total_value", "expenses", "housing")].to_list()
monthly_data["food"] = cash_flow_df.loc[:, ("total_value", "expenses", "food")].to_list()
monthly_data["shopping"] = cash_flow_df.loc[:, ("total_value", "expenses", "shopping")].to_list()
monthly_data["utilities"] = cash_flow_df.loc[:, ("total_value", "expenses", "utilities")].to_list()
monthly_data["health"] = cash_flow_df.loc[:, ("total_value", "expenses", "health")].to_list()
monthly_data["leisure"] = cash_flow_df.loc[:, ("total_value", "expenses", "leisure")].to_list()


# ============================================================================ #
# Output


# [Current month, yearly average, historical months] for each variable
data = {
    key: [[val[-1]], [np.mean(val[-13:-1])], val[-2::-1]]
    for (key, val) in monthly_data.items()}

info = {
    "startDate": [start_date.month, start_date.year],
    "endDate": [end_date.month, end_date.year]
}

output = {
    "info": info,
    "data": data}

# Data as a JSON string
data_json = json.dumps(output, indent=4)

# Saves data_json in current directory
with open(os.path.join(dirname, "./data.json"), "w") as file:
    file.write(data_json)
