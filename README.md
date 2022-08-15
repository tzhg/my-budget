# my-budget

This is a simple tool for visualizing household financial data.
A demo, using simulated data, is available [here](https://tzhg.github.io/my-budget/dist/).

The visualization shows cash, savings (both financial assets and real assets), and debt;
income and expenses, including savings- and debt-related income and expenses; and the breakdown of expenses into various categories.
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

### Terminology

For conciseness and consistency I have had to use certain terms in a less than typical way.

* **Cash**:
  * Physical cash and demand deposit accounts denominated in the local currency.
* **Savings**:
  * An item which stores value, excluding cash and durable goods.
* **Debt**:
  * An item whose value represents an obligation to pay.
* **Price index**:
    A number which records the relative value of savings or debt at a specific point in time.
* **Transaction**:
  * A change in cash.
* **Income**:
  * A positive change in cash. Excludes income related to savings or debt, unless specified.
* **Expenses**:
  * A negative change in cash. Excludes expenses related to savings or debt, unless specified.
* **Durable good**:
  * An item which may store value, but is considered an expense rather than savings.

### Recording initial cash, savings, and debt

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
            "value": 1,
            "asset_value": 1
        },
        {
            "id": "r0",
            "category": "Real",
            "value": 1,
            "asset_value": 5000
        }
    ],
    "debt": [
        {
            "id": "d0",
            "value": 1,
            "asset_value": 20000
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
  * List of initial savings (see below).
* **debt** (optional): ***array of objects***
  * List of initial debt (see below).

### Recording transactions

`data/cash-flow.csv`
| id  | date       | type            | category  | quantity | value    | reference |
|-----|------------|-----------------|-----------|----------|----------|-----------|
| 0   | 01/01/2013 | Income          |           | 1        | 3500.00  |           |
| 1   | 01/01/2013 | Expenses        | Housing   | 1        | 1700.00  |           |
| 2   | 01/01/2013 | Expenses        | Utilities | 1        | 300.00   |           |
| 3   | 01/01/2013 | Debt selling    |           | 0.01     | 20000.00 | d0        |
| 4   | 01/01/2013 | Asset expenses  |           | 1        | 198.00   | d0        |

* **id**: ***string***
  * Unique ID of transaction.
* **date**: ***string***
  * Date of transaction in DD/MM/YYYY format.
* **type**: ***string***
  * Type of transaction.
  * `Savings buying`: Records buying savings.
  * `Savings selling`: Records selling savings.
  * `Debt buying`: Records acquiring debt.
  * `Debt selling`: Records repaying debt.
  * `Income`: Records income.
  * `Expenses`: Records expenses.
  * `Savings/debt income`: Records income related to savings or debt, for instance dividends and interest received.
  * `Savings/debt expenses`: Records expenses related to savings or debt, for instance interest paid.
  * `Goods selling`: Records durable goods selling or refunding.
  * `Reimbursement`: Records expense reimbursement.
* **category** (optional): ***string***
  * Category of transaction.
  * Categories of expenses (can be left blank):
    * `Housing`: Housing.
    * `Utilities` Utilities and transport.
    * `Food`: Food and household supplies.
    * `Health`: Health and beauty.
    * `Shopping`: Durable goods.
    * `Leisure`: Leisure and hobbies.
  * Categories of savings (only required the first time savings are acquired):
    * `Financial`: Financial assets. Includes savings accounts, pensions, shares, foreign cash, and given loans.
    * `Real`: Real assets.
* **value**: ***scalar***
  * Cash value of transaction, strictly positive.
* **price_index** (optional): ***scalar***
  * Price index at given date, strictly positive.
    Only required when buying or selling savings, debt, or sold durable goods.
* **reference** (optional): ***string***
  * ID of some previous transaction.
    Only required when buying or selling existing debt or savings, selling durable goods, or reimbursing expenses.

#### Note 1: Non-cash transactions

Transactions involving savings or debt instead of cash,
such as receiving savings as a gift, or buying goods with debt,
can be recorded by converting (i.e. buying/selling) the savings or debt to cash
along with a regular cash transactions.

#### Note 2: Real assets vs durable goods

Real assets and durable goods are theoretically equivalent,
but transactions must belong to one or the other.
Personally, I limit real assets to expensive items like real estate and vehicles,
and convert sold durable goods to real assets using the `Goods selling` type.

#### Note 3: Expense cancellation

The program provides two ways of cancelling expenses,
which avoids unnecessary fluctuations in income and expenses.
When selling or refunding a durable good,
the sold portion of the expense is converted to a real asset retroactively,
which is sold when the item is sold.
When reimbursing an expense,
the reimbursed portion of the expense is converted to a financial asset retroactively,
which is sold when the expense is reimbursed.

#### Note 4: Savings/debt income and expenses

Savings/debt income and expenses theoretically includes the income and expenses from
buying and selling savings and debt.
However to prevent these transactions from dominating regular income and expenses,
they are replaced by the resulting capital gains and losses, which are calculated automatically first in first out

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

### Recording appreciation/depreciation of savings or debt (optional)

`data/asset-values/<id>.csv`, where `<id>` is the ID of savings or debt
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

* **date**: *string*
  * Any date.
* **price_index**: ***scalar***
  * Price index at given date, strictly positive.

### Dependencies

* **Python libraries**: Pandas, NumPy.
* **npm modules**: webpack, webpack-cli, css-loader, style-loader.
