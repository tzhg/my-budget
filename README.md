# my-budget

This is a program for recording and visualizing household financial data.
A demo, using simulated data, is available [here](https://tzhg.github.io/my-budget/dist/).

The web visualization plots data for assets and liabilities, income and expenses, and breakdown of expenses,
over the current month ("MTD"), the average of the last 12 months ("12M avg"), and all previous months.

The program is able to deal with many complex situations, including
 * Profits or losses from selling assets
 * Appreciation or depreciation of assets
 * Debt and interest payments
 * Refunds, and reimbursements
 * Foreign currencies and gift vouchers
 * Loans and gifts

I designed this tool for my own purposes,
to help me track my money, evaluate my spending and investments, and budget for the future.
However, I hope that it may be helpful or inspiring to others.

## How to use

```
my-budget
├── src
│   ├── data
│   │   ├── prices
│   │   │   └── <id>.csv
│   │   ├── init-assets.json
│   │   ├── transactions.csv
│   │   └── cash-snapshots.json
│   └── build-data.py
└── dist
    └── index.html
```

The script `src/build-data.py` takes the input data from directory `src/data`
and generates the data needed to make the visualization.
The visualization is created as a static website in the `dist` directory
and needs to be built using the [webpack](https://webpack.js.org/) command "npx webpack".

The input files are located in the `src/data` directory (in this repository named `src/data-simulated`).
Initial cash, savings, and debt are recorded in `init-assets.json`.
The main input file, recording all transactions, is the CSV file `transactions.csv`.
I keep this data in a separate spreadsheet, and export to CSV when needed.
There is an optional file `cash-snapshots.json` which is used to record
cash snapshots on a specific day.
The script takes into account any discrepancies between the snapshots and calculated cash
to ensure the data is accurate.
There is also an optional directory `prices` containing files with names of the form `<id>.csv`,
where `<id>` is refers to some savings or debt.
These files record price changes over time,
allowing for appreciation or depreciation.

The script also outputs some useful information:

```
Cash snapshots
--------------
08/09/2022: 10738.17 (surplus of 6.81)
09/09/2022: 10738.17
23/10/2022: 10510.84 (deficit of -5.36)
11/11/2022: 11562.41 (surplus of 1.69)
17/11/2022: 11562.41

Assets as of 31/12/2022
-----------------------
Cash: 9444.01
Savings:
  0: 5527.64
  4: 5000.00
  2: 799.47
  1: 745.73
Debt: None
```

## Dependencies

* **Python libraries**: Pandas, NumPy.
* **npm modules**: webpack, webpack-cli, css-loader, style-loader.

## Terminology

* **Cash**:
  * Physical cash and demand deposit accounts denominated in a particular currency.
* **Savings**:
  * An item which stores value, excluding cash and durable goods.
    Includes financial assets (e.g. savings accounts, pensions, shares, foreign cash, given loans) and real assets (e.g. real estate, vehicles).
* **Debt**:
  * An item whose value represents an obligation.
* **Net assets**:
  * Cash plus savings minus debt.
* **Price index**:
  * A number which records the relative value of savings or debt at a specific point in time.
* **Transaction**:
  * A change in cash.
* **Income**:
  * A positive change in cash. Excludes income related to savings or debt (e.g. dividend, interest received), unless specified.
* **Expenses**:
  * A negative change in cash. Excludes expenses related to savings or debt (e.g. interest paid), unless specified.
* **Net income**:
  * Income minus expenses, including income and expenses related to savings or debt.
* **Durable good**:
  * An item which stores value, but is considered an expense rather than savings.
    **Sold durable goods** refers retroactively to durable goods
    which are partially or fully sold or refunded.

## Input files

### `data/init-assets.json`

```json
{
    "date": "01/01/2008",
    "cash": [
        {
            "description": "Cash",
            "value": 2800.00
        },
        {
            "description": "Bank account",
            "value": 4200.00
        }
    ],
    "savings": [
        {
            "id": "0",
            "category": "Financial",
            "value": 200.00,
            "price_index": 1
        }
    ],
    "debt": [
        {
            "id": "1",
            "value": 20000.00,
            "price_index": 1
        }
    ]
}
```
* **date**: ***string***
  * Initial date in DD/MM/YYYY format.
* **cash** (optional): ***array of objects***
  * List of initial cash sources.
  * **description** (optional): ***string***
    * Description of cash source.
  * **value**: ***scalar***
    * Cash value of cash source.
* **savings** (optional): ***array of objects***
  * List of initial savings.
    * **id**: ***string***
      * Unique ID. (Unique also with respect to transaction IDs.)
    * **category**: ***string***
      * Category of savings: `Financial` or `Real`.
    * **value**: ***scalar***
      * Cash value of savings, positive.
    * **price_index**: ***scalar***
      * Price index at given date, positive.
* **debt** (optional): ***array of objects***
  * List of initial debt.
    * **id**: ***string***
      * Unique ID. (Unique also with respect to transaction IDs.)
    * **value**: ***scalar***
      * Cash value of debt, positive.
    * **price_index**: ***scalar***
      * Price index at given date, positive.

### `data/transactions.csv`

| id | date       | type                  | category  | value   | price_index | reference |
|----|------------|-----------------------|-----------|---------|-------------|-----------|
| 2  | 01/01/2008 | Income                |           | 3500.00 |             |           |
| 3  | 01/01/2008 | Expenses              | Housing   | 1700.00 |             |           |
| 4  | 01/01/2008 | Expenses              | Utilities | 300.00  |             |           |
| 5  | 01/01/2008 | Savings/debt expenses |           | 100.00  |             | 1         |
| 6  | 02/01/2008 | Debt selling          |           | 116.24  | 1           | 1         |
| 7  | 03/01/2008 | Expenses              | Food      | 36.85   |             |           |
| 8  | 03/01/2008 | Expenses              | Shopping  | 228.98  |             |           |
| 9  | 05/01/2008 | Expenses              | Food      | 36.05   |             |           |

* **id**: ***string***
  * Unique ID of transaction.
* **date**: ***string***
  * Date of transaction in DD/MM/YYYY format.
    The dates are required to be in ascending order to reduce errors. 
* **type**: ***string***
  * Type of transaction.
  * `Savings buying`: Records buying savings.
  * `Savings selling`: Records selling savings.
  * `Debt buying`: Records acquiring debt.
  * `Debt selling`: Records repaying debt.
  * `Income`: Records income.
  * `Expenses`: Records expenses.
  * `Savings/debt income`: Records income related to savings or debt.
  * `Savings/debt expenses`: Records expenses related to savings or debt.
  * `Goods selling`: Records selling of durable goods.
  * `Reimbursement`: Records reimbursement of expenses.
* **category** (optional): ***string***
  * Category of transaction for expenses or savings.
  * For expenses (can be left blank):
    `Housing`, `Utilities`, `Food`, `Health`, `Shopping` or `Leisure`.
  * For savings (only required the first time savings are acquired):
    `Financial` or `Real`.
* **value**: ***scalar***
  * Cash value of transaction, positive.
* **price_index** (optional): ***scalar***
  * Price index at given date, positive.
    Only required when buying or selling savings, debt, or sold durable goods.
* **reference** (optional): ***string***
  * ID of some previous transaction or initial savings or debt.
    Only required when buying or selling previously seen debt, savings, or sold durable goods; or reimbursing expenses.

#### Note 1: Non-cash transactions

There are many situations where cash is not involved in a transaction.
Examples include purchasing with foreign currency, receiving gift vouchers as a gift,
or buying goods with debt.
These situations can be recorded by splitting the non-cash transaction into two cash transactions.
For instance, to record an expense paid for with foreign currency,
first sell the foreign currency for cash, second use this cash to buy the expense.

#### Note 2: Real assets and durable goods

Real assets, can potentially include any durable good.
However real assets are savings, and durable goods are expenses,
and each transaction can only belong to one type.
Personally I limit real assets to expensive items like real estate and vehicles,
along with sold durable goods (see next note).

#### Note 3: Sales and reimbursements

Selling a durable good and reimbursing an expense
retroactively change the expense to a different type in order to avoid
unnecessary fluctuations in income and expenses.
When selling or refunding a durable good,
the sold portion of the expense is converted to a real asset.
When reimbursing an expense,
the reimbursed portion of the expense is converted to a financial asset.

#### Note 4: Savings/debt income and expenses

Savings/debt income and expenses should include the income and expenses from
buying and selling savings and debt.
However to prevent these transactions from dominating
regular income and expenses in the visualization,
they are replaced by the associated capital gains and losses,
which are calculated automatically first in first out.

### `data/cash-snapshots.json`

```json
[
    {
        "date": "01/02/2008",
        "cash": [
            {
                "description": "Cash",
                "value": 2861.34
            },
            {
                "description": "Bank account",
                "value": 4292.01
            }
        ]
    },
    {
        "date": "24/03/2008",
        "cash": [
            {
                "description": "Cash",
                "value": 2835.90
            },
            {
                "description": "Bank account",
                "value": 4253.86
            }
        ]
    }
]
```
* **date**: ***string***
  * Date of snapshot in DD/MM/YYYY format.
* **cash** (optional): ***array of objects***
  * List of cash sources.
  * **description** (optional): ***string***
    * Description of cash source.
  * **value**: ***scalar***
    * Cash value of cash source at start of given date.

### `prices/<id>.csv`

| date       | value              |
|------------|--------------------|
| 01/01/2013 | 1.03               |
| 02/01/2013 | 1.02               |
| 03/01/2013 | 1.1                |
| 04/01/2013 | 1.11               |
| 05/01/2013 | 1.04               |

* **date**: *string*
  * Any date.
* **price_index**: ***scalar***
  * Price index at given date, positive.
