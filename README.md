# my-budget

This is a simple tool for visualizing household financial data.
A demo, using simulated data, is available [here](https://tzhg.github.io/my-budget/dist/).

The visualization shows assets and liabilities, with breakdown of assets into cash, financial, and real;
income and expenses, of which are asset-related; and the breakdown of expenses into various categories.
It provides charts for the current month ("MTD"), the average of the last 12 months ("12M avg"), and all previous months.

I designed this tool for my own purposes,
to help me record, evaluate, and plan my expenses and investment decisions.
However, I hope that it may be helpful or inspiring to others.

To use, input your data, process it with the script `src/build-data.py`,
and use [webpack](https://webpack.js.org/) to build a static website in the `dist` directory.
The input files are located in the `data` directory (in this repository named `data-simulated`).

```
my-budget
├── src
│   ├── data
│   │   ├── asset-values (optional)
│   │   │   └── <id>.csv
│   │   ├── init-assets.json
│   │   ├── cash-flow.csv
│   │   └── cash-snapshots.json (optional)
```

### Recording initial assets

`data/init-assets.json`
```json
{
    "date": "01/01/2013",
    "cash": [
        {
            "description": "Cash",
            "value": 2800.0
        },
        {
            "description": "Bank account",
            "value": 4200.0
        }
    ],
    "savings": [
        {
            "id": "a0",
            "category": "Financial",
            "quantity": 1,
            "value": 1
        },
        {
            "id": "r0",
            "category": "Real",
            "quantity": 1,
            "value": 5000
        }
    ],
    "debt": [
        {
            "id": "d0",
            "quantity": 1,
            "value": 20000
        }
    ]
}
```

Records initial data.
* `date`: Initial date.
* `cash`: Array of initial cash sources ("cash" refers to physical cash and demand deposit accounts denominated in the local currency).
  * `description`: Description of cash source.
  * `value`: Cash value of cash source.
* `savings`: Array of initial savings (see below).
* `debt`: Array of initial debt (see below).

### Recording transactions

`data/cash-flow.csv`
| id  | date       | type            | category  | quantity | value    | reference |
|-----|------------|-----------------|-----------|----------|----------|-----------|
| 0   | 01/01/2013 | Income          |           | 1        | 3500.00  |           |
| 1   | 01/01/2013 | Expenses        | Housing   | 1        | 1700.00  |           |
| 2   | 01/01/2013 | Expenses        | Utilities | 1        | 300.00   |           |
| 3   | 01/01/2013 | Debt selling    |           | 0.01     | 20000.00 | d0        |
| 4   | 01/01/2013 | Asset expenses  |           | 1        | 198.00   | d0        |

Records transactions.
* `id`: Unique ID of transaction.
  * It is convenient to supply IDs incrementally, starting with initial data.
  * These IDs are used to refer to a transaction or asset.
* `date`: Date of transaction.
* `type`: Type of transaction (see below).
* `category`: Category of transaction within its type (see below).
  * May be blank.
* `quantity`: Quantity bought or sold.
  * Usually this is set to 1.
    Using other values can be useful when selling a portion of an owned asset.
* `value`: Cash value of transaction.
  * Always positive.
* `reference`: ID of another transaction.
  * May be blank.

### Recording cash reserves (optional)

`data/cash-snapshots.json`
```json
[
    {
        "date": "09/03/2013",
        "cash": [
            {
                "description": "Cash",
                "value": 3063.528
            },
            {
                "description": "Bank account",
                "value": 4595.292
            }
        ]
    },
    {
        "date": "29/06/2013",
        "cash": [
            {
                "description": "Cash",
                "value": 2839.03528
            },
            {
                "description": "Bank account",
                "value": 4258.55292
            }
        ]
    }
]
```
Records the amount of cash held at specific times.

The program calculates any discrepancies with calculated cash, which are then shown in Income or Expenses as errors/omissions.
The snapshot must take place at the beginning of the given day, before any changes in the amount of cash take place.

### Recording asset appreciation/depreciation (optional)

`data/asset-values/<id>.csv`
| date       | value              |
|------------|--------------------|
| 01/01/2013 | 2.01               |
| 02/01/2013 | 3.04               |
| 03/01/2013 | 4.01               |
| 04/01/2013 | 5.0                |
| 05/01/2013 | 6.07               |
| 06/01/2013 | 7.04               |
| 07/01/2013 | 8.08               |
| 08/01/2013 | 9.09               |
| 09/01/2013 | 10.06              |

Records the price of the asset with ID `<id>` over time.
* `date`: Any date.
* `value`: Value of asset at given date.

### Transaction types

#### Income and expenses

 * The types **Income** and **Expenses** record transactions not related to savings or debt.
 * Expenses are categorized as **Housing**, **Utilities**, **Food**, **Health**, **Shopping**, **Leisure**, or none.
   Expenses without a category are not shown in the breakdown of expenses chart.
 * Transactions involving assets instead of cash, such as receiving savings as a gift, or buying goods with debt,
   can be recorded by converting (i.e. buying/selling) the non-cash asset to cash
   along with a regular cash transactions.

#### Savings and debt

 * The types **Savings buying**, **Savings selling**, **Debt buying**, and **Debt selling**
   record the buying and selling of savings and debt
   ("buying debt" refers to borrowing money, and "selling debt" refers to repaying a loan).
 * Savings are categorized as **Financial** or **Real**.
   Financial assets include savings accounts, pensions, shares, foreign cash, and given loans.
   Real assets can include potentially any durable good, but for practical purposes may be limited to expensive items like real estate and vehicles,
   as well as sold goods (see **Goods selling**).
 * The first time an asset is bought or sold, `category` is required and `reference` is not.
 * For subsequent transactions, `category` is not required and `reference` must refer to the ID of the first transaction.
 * The types **Asset income** and **Asset expenses** record income and expenses related to savings and debt (i.e. "asset-related"),
   for instance dividends and interest (paid and received).
   This excludes income and expenses from buying or selling assets,
   but includes capital gains and losses, which are calculated automatically first in first out.

#### Expense cancellation

 * The type **Goods selling** records the selling or refunding a previously bought item with ID given by `reference`.
   The sold portion of the expense is converted to a real asset retroactively, which is sold when the item is sold.
 * The type **Reimbursement** records the reimbursement a previous expense with ID given by `reference`.
   The reimbursed portion of the expense is converted to a financial asset retroactively, which is sold when the expense is reimbursed.

### Dependencies

* **Python libraries**: Pandas, NumPy.
* **npm modules**: webpack, webpack-cli, css-loader, style-loader.
