# Budget visualiser

This is a simple tool for visualising household financial data.
A demo, using simulated data, is available [here](https://tzhg.github.io/my-budget/).
After providing it with the necessary data,
the program illustrates various variables over various time periods using bar charts.

Data variables:
- Assets (cash and savings) and liabilities.
- Cash flow (income, expenses, and investment profit/loss).
- Breakdown of expenses.

Time periods:
- Current month ("MTD"),
- Average of last 12 months ("12M avg"),
- All previous months.

I designed this tool for my own purposes,
to help me record, evaluate, and plan my expenses and investment decisions.
However, I hope that it may be helpful or inspiring to others.

## Details

### Recording cash

1. Cash refers to physical cash and demand deposit accounts denominated in the local currency.

2. Each row in `data/cash-input.txt` represents a cash snapshot, which is a record of the amount cash held at a specific point in time.

3. It is necessary to take a snapshot on the first day to record the initial amount of cash.
   No further snapshot are required, as future cash is calculated automatically using cash flow data.

4. For each snapshot the program calculates any discrepancies and records them as errors/omissions,
   which are included in Income or Expenses.

5. The snapshot must take place at the beginning of the given day, before any cash flow entries.

6. The amount of cash can be provided as a single number,
   or broken into sources (e.g. different bank accounts) for convenience.

### Recording savings

1. Savings refers to non-cash assets, e.g. real estate, savings accounts, pensions, shares, bonds, foreign cash.

2. There is no clear divide between real assets and consumable goods (which are recorded as an expense).
   Expensive goods which retain their value can be considered real assets.

3. In `data/savings-input.txt`, initial savings are denoted with `type="I"`,
   assets to buy with `type="B"`, and assets to sell with `type="S"`.

4. When assets are bought or sold, the quantity and value per unit are recorded.
   For fungible goods, the quantity may be the number of units bought or sold,
   and the value a price index (e.g. share price).
   For non-fungible goods, the quantity can be set to 1, and the value the total value.

5. Assets are tracked over time using a unique name.

6. Capital gains and losses are calculated first in first out.

7. Capital appreciation and depreciation can be taken into account using prices in the files `data/assets/<name>.txt`,
   where <name> is the name of the asset.
   The prices do not have to be updated daily, but must contain at least the value on the day of purchase.

8. Debt is treated as an asset with negative value. Paying off the principal is recorded as selling the asset.

### Recording cash flows

1. Cash flow refers to any movement of cash. It is divided into non-investment income and expenses, and investment profit and loss.
   These are shown on the chart as "Income", "Expenses", "Profit", and "Loss" respectively.

2. Expenses for buying savings are not recorded immediately as cash flow, but are subtracted from income when they are sold.
   This is to prevent investments from dominating regular expenses.

3. Investment profit and loss refer to cash flows relating to savings, e.g. capital gains and losses, dividends, interest.

4. Dividends and interest payments, both inbound and outbound, have to be manually recorded in `data/profit-loss-input.txt`.

5. Non-investment cash flows are recorded in `data/income-input.txt` and `data/expenses-input.txt`.

6. Expenses are categorised into six categories plus "Other".
   "Other" expenses are not shown on the breakdown of expenses chart.

7. Asset flows not involving cash, such as receiving savings as a gift, or buying goods with debt,
   can be recorded by converting (i.e. buying/selling) the non-cash asset to cash
   along with a regular cash flow.
