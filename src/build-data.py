#!/bin/bash

import os, json
from datetime import datetime
import pandas as pd
import numpy as np
from numbers import Number

pd.options.mode.chained_assignment = None
pd.set_option("display.max_rows", None)

input_date_format = "%d/%m/%Y"

# Directory of input data
data_dir = "data-simulated"
#data_dir = "data"

# Current directory
dirname = os.path.dirname(os.path.abspath(__file__))

class colours:
    default = "\033[0m"
    red = "\033[91m"
    green = "\033[92m"
    yellow = "\033[93m"
    blue = "\033[94m"
    purple = "\033[95m"

# Information about type values in cash flow data
types = {
    "expenses": {
        "name": "Expenses",
        "categories": {
            "default": {
                "name": "Default"},
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
                "name": "Leisure"}}},
    "sale": {
        "name": "Goods selling",
        "categories": {
            "default": {
                "name": "Default"}}},
    "reimbursement": {
        "name": "Reimbursement",
        "categories": {
            "default": {
                "name": "Default"}}},
    "income": {
        "name": "Income",
        "categories": {
            "default": {
                "name": "Default"}}},
    "savings_buy": {
        "name": "Savings buying",
        "base": "savings",
        "categories": {
            "default": {
                "name": "Default"},
            "financial": {
                "name": "Financial"},
            "real": {
                "name": "Real"}}},
    "savings_sell": {
        "name": "Savings selling",
        "base": "savings",
        "categories": {
            "default": {
                "name": "Default"}}},
    "debt_buy": {
        "name": "Debt buying",
        "base": "debt",
        "categories": {
            "default": {
                "name": "Default"}}},
    "debt_sell": {
        "name": "Debt selling",
        "base": "debt",
        "categories": {
            "default": {
                "name": "Default"}}},
    "sd_income": {
        "name": "Savings/debt income",
        "categories": {
            "default": {
                "name": "Default"}}},
    "sd_expenses": {
        "name": "Savings/debt expenses",
        "categories": {
            "default": {
                "name": "Default"}}}}

monthly_data = {}


# Number of months between start date and datetime object d
def num_months(d):
    return (d.year - init_date.year) * 12 + d.month - init_date.month


# Calculates total cash from multiple sources
def total_cash(cash_array):
    return sum([obj["value"] for obj in cash_array])


def validate_value(x, a, b):
    if not isinstance(x, Number):
        raise ValueError(f"{a}: {b} ({x}) not a valid number")
        return False
    if x < 0:
        raise ValueError(f"{a}: {b} negative")
        return False
    return True

# ============================================================================ #
# Loads initial cash, savings, and debt data

with open(os.path.join(dirname, f"./{data_dir}/init-assets.json"), "r") as file:
    init_assets = json.load(file)

if not isinstance(init_assets, dict):
    raise ValueError("init-assets.json: JSON not a valid object")

if "date" not in init_assets:
    raise ValueError("init-assets.json: 'date' not valid key in JSON object")
else:
    try:
        init_date = datetime.strptime(init_assets["date"], input_date_format)
    except ValueError:
        raise ValueError(f"init-assets.json: Object.date ({init_assets['date']}) not valid date")

if "cash" in init_assets:
    if not isinstance(init_assets["cash"], list):
        raise ValueError("init-assets.json: Object.cash not valid array")
    else:
        for i, asset in enumerate(init_assets["cash"]):
            if "value" not in asset:
                raise ValueError(f"init-assets.json: 'value' not valid key in Object.cash[{i}]")
            else:
                validate_value(asset["value"], "init-assets.json", f"Object.cash[{i}].value")
    init_cash = total_cash(init_assets["cash"])
else:
    init_cash = 0

if "savings" in init_assets:
    if not isinstance(init_assets["savings"], list):
        raise ValueError("init-assets.json: Object.savings not valid array")
    else:
        for i, asset in enumerate(init_assets["savings"]):
            if "category" not in asset:
                raise ValueError(f"init-assets.json: 'category' not valid key in Object.savings[{i}]")
            elif asset["category"] not in [obj["name"] for _, obj in types["savings_buy"]["categories"].items()]:
                raise ValueError(f"init-assets.json: Object.savings[{i}].category ({asset['category']}) not valid category")

            for l in ["value",  "price_index"]:
                if l not in asset:
                    raise ValueError(f"init-assets.json: '{l}' not valid key in Object.savings[{i}]")
                else:
                    validate_value(asset[l], "init-assets.json", f"Object.savings[{i}].{l}")

    init_savings = init_assets["savings"].copy()
else:
    init_savings = []

if "debt" in init_assets:
    if not isinstance(init_assets["debt"], list):
        raise ValueError("init-assets.json: Object.debt not valid array")
    else:
        for i, asset in enumerate(init_assets["debt"]):
            for l in ["value",  "price_index"]:
                if l not in asset:
                    raise ValueError(f"init-assets.json: '{l}' not valid key in Object.debt[{i}]")
                else:
                    validate_value(asset[l], "init-assets.json", f"Object.debt[{i}].{l}")
    init_debt = init_assets["debt"].copy()
else:
    init_debt = []

# Replaces type and category names with standard form
for asset in init_savings:
    for cat, obj in types["savings_buy"]["categories"].items():
        asset["category"] = asset["category"].replace(obj["name"], cat)

# ============================================================================ #
# Loads cash snapshot data

snapshot_flag = False

try:
    with open(os.path.join(dirname, f"./{data_dir}/cash-snapshots.json"), "r") as file:
        cash_snapshots = json.load(file)
except FileNotFoundError:
    pass
else:
    snapshot_flag = True

if snapshot_flag:
    for i, snapshot in enumerate(cash_snapshots):
        if "date" not in snapshot:
            raise ValueError("cash-snapshots.json: 'date' not valid key in JSON object")
        else:
            try:
                snapshot["date"] = datetime.strptime(snapshot["date"], input_date_format)
            except ValueError:
                raise ValueError(f"cash-snapshots.json: Object[{i}].date ({snapshot['date']}) not valid date")
            else:
                if snapshot["date"] < init_date:
                    raise ValueError(f"cash-snapshots.json: Object[{i}].date ({snapshot['date']}) is before initial date ({init_date})")

        if "cash" in init_assets:
            if not isinstance(snapshot["cash"], list):
                raise ValueError(f"cash-snapshots.json: Object[{i}].cash not valid array")
            else:
                for j, asset in enumerate(snapshot["cash"]):
                    if "value" not in asset:
                        raise ValueError(f"cash-snapshots.json: 'value' not valid key in Object[{i}].cash[{j}]")
                    else:
                        validate_value(asset["value"], "cash-snapshots.json", f"Object[{i}].cash[{j}].value")
            snapshot["cash"] = total_cash(snapshot["cash"])
        else:
            snapshot["cash"] = 0

    cash_snapshots = sorted(cash_snapshots, key=lambda d: d["date"])

# ============================================================================ #
# Loads cash flow data

cash_flow_df = pd.read_csv(os.path.join(dirname, f"./{data_dir}/transactions.csv"))

if not "id" in cash_flow_df.columns:
    raise ValueError(f"transactions.csv: 'id' not valid column")
else:
    cash_flow_df["id"] = cash_flow_df["id"].astype("string")
    id_cf = cash_flow_df["id"].tolist()
    id_inits = [asset["id"] for asset in init_savings]
    id_initd = [asset["id"] for asset in init_debt]
    id_list = id_cf + id_inits + id_initd

    # Finds duplicate IDs
    seen = set()
    dupes = [x for x in id_list if x in seen or seen.add(x)]

    if len(dupes) > 0:
        raise ValueError(f"init-assets.json, transactions.csv: IDs ({dupes}) not unique")

    cash_flow_df = cash_flow_df.set_index("id")
if not "date" in cash_flow_df.columns:
    raise ValueError(f"transactions.csv: 'date' not valid column")
else:
    cash_flow_df["date"] = cash_flow_df["date"].astype("string")
    try:
        cash_flow_df["date"] = pd.to_datetime(cash_flow_df["date"], format=input_date_format)
    except ValueError:
        raise ValueError(f"transactions.csv: column 'date' does not contain valid dates")
    else:
        if cash_flow_df["date"].tolist() != cash_flow_df["date"].sort_values().tolist():
            raise ValueError(f"transactions.csv: dates not in ascending order")
        cash_flow_df["month"] = num_months(cash_flow_df["date"].dt)
        if cash_flow_df["date"].iat[0] < init_date:
            raise ValueError(f"cash-snapshots.json: Object[{i}].date ({snapshot['date']}) is before initial date ({init_date})")
if not "type" in cash_flow_df.columns:
    raise ValueError(f"transactions.csv: column 'type' not valid column")
else:
    cash_flow_df["type"] = cash_flow_df["type"].astype("string")
if not "category" in cash_flow_df.columns:
    raise ValueError(f"transactions.csv: 'category' not valid column")
else:
    cash_flow_df["category"] = cash_flow_df["category"].astype("string")
if not "value" in cash_flow_df.columns:
    raise ValueError(f"transactions.csv: column 'value' not valid column")
else:
    cash_flow_df["value"] = cash_flow_df["value"].astype("float64")
if not "price_index" in cash_flow_df.columns:
    raise ValueError(f"transactions.csv: column 'price_index' not valid column")
else:
    cash_flow_df["price_index"] = cash_flow_df["price_index"].astype("float64")
if not "reference" in cash_flow_df.columns:
    raise ValueError(f"transactions.csv: column 'reference' not valid column")
else:
    cash_flow_df["reference"] = cash_flow_df["reference"].astype(pd.Int64Dtype()).astype("string")

cash_flow_df["category"].fillna("Default", inplace=True)

for i, row in cash_flow_df.iterrows():
    type = None
    for key, obj in types.items():
        if row["type"] == obj["name"]:
            type = key
    if type == None:
        raise ValueError(f"transactions.csv: ({i}, 'type') does not contain valid type")
    if row["category"] not in [obj["name"] for _, obj in types[type]["categories"].items()]:
        raise ValueError(f"transactions.csv: ({i}, 'category') does not contain valid categories")
    validate_value(row["value"], "transactions.csv", f"({i}, 'value')")

if snapshot_flag:
    end_date = max(cash_snapshots[-1]["date"], cash_flow_df["date"].iat[-1])
else:
    end_date = cash_flow_df["date"].iat[-1]
no_months = num_months(end_date) + 1

# Replaces type and category names with standard form
for type, obj in types.items():
    cash_flow_df["type"].replace(to_replace={obj["name"]: type}, inplace=True)
    cash_flow_df["category"].replace(to_replace={obj2["name"]: cat for cat, obj2 in obj["categories"].items()}, inplace=True)

# Validates price index and reference
for i, row in cash_flow_df.iterrows():
    if pd.isna(row["price_index"]):
        if row["type"] == "savings_buy" or row["type"] == "savings_sell" or row["type"] == "debt_buy" or row["type"] == "debt_sell" or row["type"] == "sale":
            raise ValueError(f"transactions.csv: ({i}, 'price_index') missing")
    else:
        validate_value(row["price_index"], "transactions.csv", f"({i}, 'price_index')")
        if row["type"] == "income" or row["type"] == "reimbursement":
            raise ValueError(f"transactions.csv: ({i}, 'price_index') not blank")
        if (row["type"] == "savings_buy" or row["type"] == "debt_buy") and row["price_index"] == 0:
            raise ValueError(f"transactions.csv: ({i}, 'price_index') zero")

    if pd.isna(row["reference"]):
        if row["type"] == "savings_sell" or row["type"] == "debt_sell":
            raise ValueError(f"transactions.csv: ({i}, 'reference') missing")
        if (row["type"] == "savings_buy" or row["type"] == "savings_sell") and row["category"] == "default":
            raise ValueError(f"transactions.csv: ({i}, 'category') missing")
    else:
        if row["type"] == "income":
            raise ValueError(f"transactions.csv: ({i}, 'reference') not blank")
        valid_ref = False
        for asset in init_savings:
            if asset["id"] == row["reference"]:
                valid_ref = True
                ref_obj = {
                    "type": "savings",
                    "category": asset["category"],
                    "price_index": asset["price_index"]}
                break
        if not valid_ref:
            for asset in init_debt:
                if asset["id"] == row["reference"]:
                    valid_ref = True
                    ref_obj = {
                        "type": "debt",
                        "price_index": asset["price_index"]}
                    break
        if not valid_ref:
            for id in cash_flow_df.index:
                if id == row["reference"]:
                    valid_ref = True
                    ref_obj = {
                        "type": cash_flow_df.at[id, "type"],
                        "category": cash_flow_df.at[id, "category"],
                        "price_index": cash_flow_df.at[id, "price_index"]}
                    break
        if valid_ref:
            if row["type"] == "savings_buy" or row["type"] == "savings_sell":
                if row["category"] != "default":
                    raise ValueError(f"transactions.csv: ({i}, 'category') not blank")
                if ref_obj["type"] != "savings_buy" and ref_obj["type"] != "savings_sell" and ref_obj["type"] != "savings":
                    raise ValueError(f"transactions.csv: (reference of {i}, 'type') does not contain correct type)")
                elif ref_obj["category"] == "default":
                    raise ValueError(f"transactions.csv: (reference of {i}, 'category') missing")
            elif row["type"] == "debt_buy" or row["type"] == "debt_sell":
                if ref_obj["type"] != "debt_buy" and ref_obj["type"] != "debt_sell" and ref_obj["type"] != "debt":
                    raise ValueError(f"transactions.csv: (reference of {i}, 'type') does not contain correct type)")
            elif row["type"] == "sale" or row["type"] == "reimbursement":
                if ref_obj["type"] != "expenses":
                    raise ValueError(f"transactions.csv: (reference of {i}, 'type') does not contain correct type)")
                if row["type"] == "sale" and pd.isna(ref_obj["price_index"]):
                    raise ValueError(f"transactions.csv: (reference of {i}, 'price_index') missing)")
        else:
            raise ValueError(f"transactions.csv: ({i}, 'reference') does not contain valid reference")

# ============================================================================ #
# Loads price data

prices_df = {}

try:
    prices_dir = os.listdir(os.path.join(dirname, f"./{data_dir}/prices"))
except FileNotFoundError:
    pass
else:
    for file in prices_dir:
        id = os.path.splitext(os.fsdecode(file))[0]
        av_df = pd.read_csv(os.path.join(dirname, f"./{data_dir}/prices/{id}.csv"))

        if not "date" in av_df.columns:
            raise ValueError(f"prices/{id}.csv: 'date' not valid column")
        else:
            av_df["date"] = av_df["date"].astype("string")
            try:
                av_df["date"] = pd.to_datetime(av_df["date"], format=input_date_format)
            except ValueError:
                raise ValueError(f"prices/{id}.csv: column 'date' does not contain valid dates")
            else:
                av_df = av_df.sort_values(by=["date"])
                av_df["month"] = num_months(av_df["date"].dt)


        if not "price_index" in av_df.columns:
            raise ValueError(f"prices/{id}.csv: column 'price_index' not valid column")
        else:
            av_df["price_index"] = av_df["price_index"].astype("float64")
            for i, row in av_df.iterrows():
                validate_value(row["price_index"], f"prices/{id}.csv", f"({i}, 'price_index')")
        prices_df[id] = av_df

# ============================================================================ #
# Cash, savings, and debt


def add_price(id, date, price):
    for date2 in prices_df[id]["date"]:
        if date == date2:
            return

    new_value_df = pd.DataFrame(
        [[date, price, num_months(date)]],
        columns=["date", "price_index", "month"])

    prices_df[id] = pd.concat([prices_df[id], new_value_df])
    prices_df[id] = prices_df[id].sort_values(by=["date"])


eo_list = []
cg_list = []
ec_list = []

monthly_data["cash"] = []
monthly_data["financial"] = []
monthly_data["real"] = []
monthly_data["debt"] = []

snap_idx = 0
month_idx = 0

# Tracks cash, savings, and debt over time
portfolio = {
    "cash": init_cash,
    "savings": init_savings,
    "debt": init_debt}

# Debt is treated like savings with negative price and value
for asset in portfolio["debt"]:
    asset["value"] *= -1
    asset["price_index"] *= -1

# Adds initial prices to prices_df
for asset in portfolio["savings"] + portfolio["debt"]:
    if asset["id"] in prices_df:
        add_price(asset["id"], init_date, asset["price_index"])


def finish_month():
    global monthly_data, portfolio, month_idx

    monthly_data["cash"].append(portfolio["cash"])

    financial_count = 0
    real_count = 0
    debt_count = 0

    for obj in portfolio["savings"]:
        if obj["id"] in prices_df:
            new_value = prices_df[obj["id"]][prices_df[obj["id"]]["month"] <= month_idx].iloc[-1]["price_index"]
            curr_value = round(obj["value"] * new_value / obj["price_index"], 2)
        else:
            curr_value = obj["value"]

        if obj["category"] == "financial":
            financial_count += curr_value
        elif obj["category"] == "real":
            real_count += curr_value

    for obj in portfolio["debt"]:
        if obj["id"] in prices_df:
            new_value = prices_df[obj["id"]][prices_df[obj["id"]]["month"] <= month_idx].iloc[-1]["price_index"]
            curr_value = round(obj["value"] * new_value / obj["price_index"], 2)
        else:
            curr_value = obj["value"]

        debt_count -= curr_value

    monthly_data["financial"].append(financial_count)
    monthly_data["real"].append(real_count)
    monthly_data["debt"].append(debt_count)

    month_idx += 1


def finish_snapshot():
    global cash_snapshots, portfolio, snap_idx

    # Calculates errors/omissions
    eo = cash_snapshots[snap_idx]["cash"] - portfolio["cash"]
    eo_list.append(eo)

    # Prepares next snapshot
    portfolio["cash"] = cash_snapshots[snap_idx]["cash"]
    snap_idx += 1


def snapshot_output(i):
    global cash_snapshots

    date_str = datetime.strftime(cash_snapshots[i]["date"], input_date_format)

    if eo_list[i] >= 0.005:
        eo_output = f" ({colours.green}surplus{colours.default} of {colours.yellow}{eo_list[i]:.2f}{colours.default})"
    elif eo_list[i] <= -0.005:
        eo_output = f" ({colours.red}deficit{colours.default} of {colours.yellow}{eo_list[i]:.2f}{colours.default})"
    else:
        eo_output = ""
    
    print(f"{date_str}: {colours.yellow}{cash_snapshots[i]['cash']:.2f}{colours.default}{eo_output}")


# Durable goods sales and reimbursements
exp_canc_df = cash_flow_df[cash_flow_df["type"].isin(["sale", "reimbursement"])]
for i, row in exp_canc_df.iterrows():
    id = row["reference"]
    if row["type"] == "sale":
        price_b = cash_flow_df.at[id, "price_index"]
        price_s = row["price_index"]
        cat = "real"
    elif row["type"] == "reimbursement":
        price_b = 1
        price_s = 1
        cat = "financial"

    if row["value"] == 0:
        sav_buy_value = 0
    else:
        sav_buy_value = row["value"] * price_b / price_s

    cash_flow_df.at[id, "value"] -= sav_buy_value

    cash_flow_df.drop(i, inplace=True)

    ec_list.append([i + "B", cash_flow_df.at[id, "date"], "savings_buy", cat, sav_buy_value, price_b, None])
    ec_list.append([i + "S", row["date"], "savings_sell", None, row["value"], price_s, i + "B"])

if len(ec_list) > 0:
    exp_canc_assets_df = pd.DataFrame(
        ec_list,
        columns=["id", "date", "type", "category", "value", "price_index", "reference"])
    exp_canc_assets_df = exp_canc_assets_df.set_index("id")
    exp_canc_assets_df["month"] = num_months(exp_canc_assets_df["date"].dt)

    cash_flow_df = pd.concat([cash_flow_df, exp_canc_assets_df])

    cash_flow_df = cash_flow_df.sort_values(by=["date"])

for i, row in cash_flow_df.iterrows():
    # Debt as negative savings
    if row["type"] == "debt_buy" or row["type"] == "debt_sell":
        row["value"] *= -1
        row["price_index"] *= -1

    # Negative transactions
    if row["type"] == "expenses" or row["type"] == "sd_expenses" or row["type"] == "savings_buy" or row["type"] == "debt_buy":
        row["value"] *= -1

    while snapshot_flag and snap_idx < len(cash_snapshots) and row["date"] >= cash_snapshots[snap_idx]["date"]:
        # Finishes snapshot
        finish_snapshot()

    while row["month"] > month_idx:
        # Finishes month
        finish_month()

    if row["value"] == 0:
        continue

    # Updates cash
    portfolio["cash"] += row["value"]

    if row["type"] == "savings_buy" or row["type"] == "debt_buy":
        base = types[row["type"]]["base"]

        if not pd.isnull(row["reference"]):
            # If savings/debt already seen
            id = row["reference"]
            if base in init_assets:
                for asset in init_assets[base]:
                    # Searches for ID in initial savings/debt
                    if asset["id"] == id:
                        cat = asset["category"]
                        break
            if id in cash_flow_df.index:
                # Searches for ID in transactions
                cat = cash_flow_df.at[id, "category"]
        else:
            # If savings/debt unseen
            id = i
            cat = row["category"]

        portfolio[types[row["type"]]["base"]].append({
            "id": id,
            "category": cat,
            "value": -row["value"],
            "price_index": row["price_index"]})

        if id in prices_df:
            add_price(id, row["date"], row["price_index"])
    elif row["type"] == "savings_sell" or row["type"] == "debt_sell":
        base = types[row["type"]]["base"]

        # Remaining value to sell
        remaining = row["value"]

        for asset in portfolio[base]:
            if asset["id"] == row["reference"]:
                price_change = row["price_index"] / asset["price_index"]

                # Value at sale of the quantity sold
                sell_value = asset["value"] * price_change
                sell_value = max(sell_value, -abs(remaining))
                sell_value = min(sell_value, abs(remaining))

                # Value at purchase of the quantity sold
                # This may not always be a whole number of cents if the quantity is fractional
                purchase_value = round(sell_value / price_change, 2)

                asset["value"] -= purchase_value
                remaining -= sell_value

                net_gain = sell_value - purchase_value

                if net_gain != 0:
                    cg_list.append([row["date"], row["reference"], net_gain])

                if remaining == 0:
                    break

                if asset["id"] in prices_df:
                    add_price(asset["id"], row["date"], row["price_index"])

        # Removes unowned savings/debt
        for asset in portfolio[base]:
            if asset["value"] == 0:
                portfolio[base].remove(asset)

while no_months > month_idx:
    # Adds final months
    finish_month()

while snapshot_flag and snap_idx < len(cash_snapshots):
    # Adds final snapshots
    finish_snapshot()

if snapshot_flag and len(eo_list) > 0:
    # DataFrame of errors/omissions
    eo_df = pd.DataFrame(
        [
            [cash_snapshots[i]["date"], "income", "default", val] if val > 0
            else
            [cash_snapshots[i]["date"], "expenses", "defaut", -val]
            for i, val in enumerate(eo_list)],
        columns=["date", "type", "category", "value"])

    eo_df["month"] = num_months(eo_df["date"].dt)

    # Adds errors/omissions to cash flow DataFrame
    cash_flow_df = pd.concat([cash_flow_df, eo_df], ignore_index=True)

if len(cg_list) > 0:
    # DataFrame of capital gains/losses
    cg_df = pd.DataFrame(
        [
            [x[0], "sd_income", "default", x[2], x[1]]
            if x[2] > 0
            else
            [x[0], "sd_expenses", "default", -x[2], x[1]]
            for x in cg_list],
        columns=["date", "type", "category", "value", "reference"])

    cg_df["month"] = num_months(cg_df["date"].dt)

    # Adds capital gains/losses to cash flow DataFrame
    cash_flow_df = pd.concat([cash_flow_df, cg_df], ignore_index=True)

    cash_flow_df = cash_flow_df.sort_values(by=["date"])

def portfolio_output():
    savings_obj = {
        "savings": {},
        "debt": {}
    }

    for l in ["savings", "debt"]:
        for obj in portfolio[l]:
            if obj["id"] in prices_df:
                new_value = prices_df[obj["id"]].iloc[-1]["price_index"]
                curr_value = round(obj["value"] * new_value / obj["price_index"], 2)
            else:
                curr_value = obj["value"]

            if obj["id"] in savings_obj[l]:
                savings_obj[l][obj["id"]] += curr_value
            else:
                savings_obj[l][obj["id"]] = curr_value
        savings_obj[l]

    if portfolio["cash"] > 0:
        print(f"Cash: {colours.yellow}{portfolio['cash']:.2f}{colours.default}")
    else:
        print(f"Cash: None")
    if len(savings_obj["savings"]) > 0:
        print(f"Savings:")
        asset_list = sorted(
            savings_obj["savings"].items(),
            key=lambda x: x[1],
            reverse=True)
        for (key, val) in asset_list:
            print(f"  {key}: {colours.blue}{val:.2f}{colours.default}")
    else:
        print("  Savings: None")
    if len(savings_obj["debt"]) > 0:
        print(f"Debt:")
        asset_list = sorted(
            savings_obj["debt"].items(),
            key=lambda x: x[1],
            reverse=True)
        for (key, val) in asset_list:
            print(f"  {key}: {colours.purple}{val:.2f}{colours.default}")
    else:
        print("Debt: None")
    
# ============================================================================ #
# Income and expenses

cash_flow_df.drop(["price_index", "reference"], axis=1, inplace=True)

# Ensures every type and category are present
null_rows = [[
        [init_date, type, cat, 0, 0]
        for cat, obj2 in obj["categories"].items()]
    for type, obj in types.items()]
null_df = pd.DataFrame(
    [x for y in null_rows for x in y],
    columns=["date", "type", "category", "month", "value"])
cash_flow_df = pd.concat([cash_flow_df, null_df])

# Aggregates entries by month and category
cash_flow_df = cash_flow_df.groupby(["month", "type", "category"]).sum()

# Reshapes df to show categories as columns
cash_flow_df = cash_flow_df.unstack(["type", "category"], fill_value=0)

monthly_data["income"] = cash_flow_df.loc[:, ("value", "income", "default")].to_list()
monthly_data["expenses"] = cash_flow_df.loc[:, ("value", "expenses", slice(None))].sum(axis=1).to_list()
monthly_data["sdincome"] = cash_flow_df.loc[:, ("value", "sd_income", "default")].to_list()
monthly_data["sdexpenses"] = cash_flow_df.loc[:, ("value", "sd_expenses", "default")].to_list()

monthly_data["netAssets"] = [
    monthly_data["cash"][i] + monthly_data["financial"][i] + monthly_data["real"][i] - monthly_data["debt"][i]
    for i in range(no_months)];

monthly_data["netIncome"] = [
    monthly_data["income"][i] + monthly_data["sdincome"][i] - monthly_data["expenses"][i] - monthly_data["sdexpenses"][i]
    for i in range(no_months)];

monthly_data["housing"] = cash_flow_df.loc[:, ("value", "expenses", "housing")].to_list()
monthly_data["food"] = cash_flow_df.loc[:, ("value", "expenses", "food")].to_list()
monthly_data["shopping"] = cash_flow_df.loc[:, ("value", "expenses", "shopping")].to_list()
monthly_data["utilities"] = cash_flow_df.loc[:, ("value", "expenses", "utilities")].to_list()
monthly_data["health"] = cash_flow_df.loc[:, ("value", "expenses", "health")].to_list()
monthly_data["leisure"] = cash_flow_df.loc[:, ("value", "expenses", "leisure")].to_list()

# ============================================================================ #
# Output

title_1 = "Cash snapshots"
title_2 = f"Assets as of {datetime.strftime(end_date, input_date_format)}"

print(f"\n{title_1}\n{'-' * len(title_1)}")

# Prints last 5 cash snapshots
for i in range(5):
    snapshot_output(len(eo_list) - 5 + i)
    
print(f"\n{title_2}\n{'-' * len(title_2)}")

# Prints portfolio
portfolio_output()

# [Current month, yearly average, historical months] for each variable
data = {
    key: [[val[-1]], [np.mean(val[-13:-1])], val[-2::-1]]
    for (key, val) in monthly_data.items()}

info = {
    "startDate": [init_date.month, init_date.year],
    "endDate": [end_date.month, end_date.year]
}

output = {
    "info": info,
    "data": data}



# Data as a JSON string (loads to convert floats to strings)
data_json = json.dumps(json.loads(json.dumps(output), parse_float=lambda x: round(float(x), 2)), indent=4)

# Saves data_json in current directory
with open(os.path.join(dirname, "./data.json"), "w") as file:
    file.write(data_json)
