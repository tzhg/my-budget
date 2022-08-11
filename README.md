# my-budget

This is a simple tool for visualising household financial data.
A demo, using simulated data, is available [here](https://tzhg.github.io/my-budget/dist/).
After providing it with the necessary data,
the program illustrates various variables over various time periods using bar charts.

Data variables:
- Assets (cash, financial, and real) and liabilities.
- Cash flow (income, expenses, and investment profit/loss).
- Breakdown of expenses.

Time periods:
- Current month ("MTD").
- Average of last 12 months ("12M avg").
- All previous months.

I designed this tool for my own purposes,
to help me record, evaluate, and plan my expenses and investment decisions.
However, I hope that it may be helpful or inspiring to others.

## How to use

1. Create directory and add your data (see `src/data-simulated` for an example).
2. Change `data-dir` variable in `src/build-data.py` to point to your data directory.
2. Run `src/build-data.py` to build `src/data.json`.
3. Run `npm run build` to build static website in `dist` directory.

### Dependencies

* **Python libraries**: Pandas, NumPy.
* **npm modules**: webpack, webpack-cli, css-loader, style-loader.

## Details

### Recording cash

*Cash* refers to physical cash and demand deposit accounts denominated in the local currency.
Cash snapshots are records of the amount of cash held at a specific time.
For each snapshot the program calculates any discrepancies and records them as errors/omissions,
which are included either in Income or Expenses.

* `cash-input.csv` records cash snapshots, and has columns **date** and **cash**.

* **date** is the date of the snapshot.
  It is assumed to take place at the beginning of the day, before any changes in the amount of cash.

* **cash** is the amount of cash, and can be provided as a single number,
  or broken into sources (e.g. different bank accounts) for convenience.

* It is necessary to take a snapshot on the first day to record the initial amount of cash.
  No further snapshots are required, as future cash is calculated automatically using cash flow data.

### Recording savings

*Savings*, or *investment*, refers to non-cash assets, e.g. real estate, savings accounts, pensions, shares, bonds, foreign cash.
There is no clear divide between real assets and consumable goods (which are recorded as an expense).
Expensive goods which retain their value can be considered real assets.

* `savings-input.csv` records the buying and selling of savings, and has columns **date**, **type**, **name**, **quantity**, and **value**.

* `assets/<name>.csv` records the price of the savings with id `<name>` over time, and has columns **date** and **value**.

* `savings-info.csv` records information about savings, and has columns **name**, **category**, and **description**.

* **date** refers to the date of transaction.
  The total amount bought or sold in the local currency is split into
  the number of units (**quantity**) and the value per unit (**value**).
  This split is fairly arbitrary.
  For fungible goods, the quantity could be the number of units bought or sold,
  and the value a price index (e.g. share price).
  For non-fungible goods, the quantity could be set to 1, and the value the total value.

* **type** signifies if the savings are bought ("B"), sold ("S"), or initial savings on the day of the first cash snapshot ("I").

* **name** is a unique identifier for the asset.

* Debt is treated as an asset with negative value.
  This implies that getting a loan is recorded as buying an asset,
  and paying off the principal is recorded as selling it.

* The files `assets/<name>.csv` are optional, and allow the unit price (**value**) to change over time,
  taking into account capital appreciation or depreciation.

* Each asset is given a category (**category**), either `financial`, `real`, or `debt`.

* The given asset descriptions (**descriptions**) are for personal reference.

### Recording cash flows

*Cash flow* refers to any movement of cash. It is divided into non-investment income and expenses, and investment profit and loss.
Investment profit and loss refer to cash flows relating to savings, e.g. capital gains and losses, dividends, and interest.
Capital gains and losses are calculated first in first out.

* `expenses-input.csv` records non-investment expenses, and has columns **date**, **category**, **value**.

* `income-input.csv` records non-investment income, and has columns **date**, **value**.

* `profit-loss-input.csv` records investment profit and loss, and has columns **date**, **name**, **value**.

* **date** refers to the date of transaction, and **value** to the amount lost or gained, in the local currency.

* Expenses for buying savings are not recorded immediately as cash flow, but are subtracted from income when they are sold.
  This is to prevent investments from dominating regular expenses.

* Expenses are categorised into six categories plus "Other" (**category**).
  "Other" expenses are not shown on the breakdown of expenses chart.

* Asset flows not involving cash, such as receiving savings as a gift, or buying goods with debt,
  can be recorded by converting (i.e. buying/selling) the non-cash asset to cash
  along with a regular cash flow.


## To do

* Data validation
