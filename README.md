# Finance Tracker
Finance Tracker is a light weight web app that allows you to track your Finance operations and its return on investment.

![Finance Tracker preview](/doc/finance-tracker-preview.png?raw=true "Finance Tracker Preview")


## How It Works
Finance Tracker allows you create portfolios of assets.
Each asset will contain operations such as BUY, SELL or DIVIDENDS (or interests).
By tracking these operations you will be able to measure the profitability of your portfolio.

### Portfolio
Portfolio is the base system. You can hold multiple portfolios and each of them is a clean state and unit of storage.

### Assets
Assets are the main entities of the system. It represents financial instruments such as stocks, options, futures, etc.

Assets contain basic information such as the asset name, the currency and its current price.

Note: at the moment, the current price is manually updated.
In the future, APIs can be added to auto-update it and keep track of the assets in real time.

### Operations
Operations are actions performed in an asset to modify its position or returns:
- **BUY**: you have acquired more units of the asset.
- **SELL**: you have get rid of some units of the asset.
- **DIVIDENDS**: you have gotten dividend from the asset.

While it is very structure after stocks, it can be used for any type of assets.
For example, if you acquire a deposit for USD10,000, you can register a 10,000 BUY operation.
When you receive the interests, you can add a DIVIDEND operation for the value.
Once you receive the principal, you deduct it with a SELL operation.

## Metrics

There are different metrics

- **Position**: how many units of the asset you currently own.
- **Market Value**: current value of the position you are holding. Calculated as: `position * current price`.
- **Realized P&L**: profit or loss in currency of sold units. Calculated as: `value of sold units - cost of sold units`.
- **Realized ROI**: return on investment of sold units. Calculated as: `realized p&l / cost of sold units`.
- **Unrealized P&L**: profit or loss in currency of current position. Calculated as: `market value - cost of units hold`.
- **Unrealized ROI**: return on investment of current position. Calculated as: `unrealized p&l / cost of units hold`.
- **Opportunity P&L**: potential profit or loss of sold units, if you hadn't sold them. Calculated as: `current market value of sold units - value of sold units at sell price`.
- **Opportunity ROI**: potential return on investment, if you hadn't sold the units. Calculated as: `opportunity P&L / value of sold units at sell price`.
- **Dividends**: total dividends/interests received from investment.
- **Dividend Yield**: dividends received per dollar invested. Calculated as: `dividends / value of dividend units held`.


At the moment, the metrics are calculated using an average price model.
However, other models such as FIFO, LIFO, minimize or maximize gain could be used too adapting the solution.


## Technical Details

The solution is built in Python and uses `Flask` for the web server.

At the moment, there is no need for a database. The state is kept using local file storages with `pickle` module.

The solution is built using an MVC approach where `models`, `routes` and `services` represent each of the parts of the system.
