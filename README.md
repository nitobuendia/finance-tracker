# Finance Tracker
Finance Tracker is a light weight web app that allows you to track your Finance investments and its return.

![Finance Tracker preview](/doc/finance-tracker-preview.png?raw=true "Finance Tracker Preview")

*Note*: this is not to track your expenses, but your investments.

## How It Works
Finance Tracker allows you create portfolios of assets.
Each asset will contain operations such as BUY, SELL or DIVIDENDS (or interests).
By tracking these operations you will be able to measure the profitability of your portfolio.

### Portfolio
Portfolio is the base system. You can hold multiple portfolios and each of them is a clean state and unit of storage.

### Assets
Assets are the main entities of the system. It represents financial instruments such as stocks, options, futures, etc.

Assets contain basic information such as the asset name, the currency and its current price.

Note: the price does not automatically update. You can update it manually or make an API request to update it based on Yahoo Finance data. For more details, read the API Endpoints section.

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

## API Endpoints

The tool does not currently have a UI to allow adding and editing details. As such, HTTP calls (i.e. API-like) needs to be used instead. 

### Endpoints
The [documentation of the available endpoints is on this website](https://documenter.getpostman.com/view/7379488/Szt789gi?version=latest).

### Considerations
1. The base URL for the solution is `http://localhost:99` or `http://127.0.0.1:99`, you may need to change this if you run it from a different IP address, server or port.
1. When you see a unique id (UUID) like `a699c7f7-96a4-4681-b8ce-b14dbc31bdf5`, it would usually refer to the ID of the item previously on the URL. Examples:
    * On `http://127.0.0.1:99/api/portfolios/a699c7f7-96a4-4681-b8ce-b14dbc31bdf5/`
        * `a699c7f7-96a4-4681-b8ce-b14dbc31bdf5/` represents the portfolio id.
    * On `http://127.0.0.1:99/api/portfolios/a699c7f7-96a4-4681-b8ce-b14dbc31bdf5/assets/NASDAQ:AMZN/`:
        * `a699c7f7-96a4-4681-b8ce-b14dbc31bdf5/` represents the portfolio id.
        * `NASDAQ:AMZN` represents the asset id.
    * On `http://127.0.0.1:99/api/portfolios/a699c7f7-96a4-4681-b8ce-b14dbc31bdf5/operations/91dddba6-c308-40e8-a921-b1deb8ad70ea/`:
        * `a699c7f7-96a4-4681-b8ce-b14dbc31bdf5/` represents the portfolio id.
        * `91dddba6-c308-40e8-a921-b1deb8ad70ea` represents the operation id.

## Technical Details

The solution is built in Python and uses `Flask` for the web server.

At the moment, there is no need for a database. The state is kept using local file storages with `pickle` module.

The solution is built using an MVC approach where `models`, `routes` and `services` represent each of the parts of the system.

## Sponsoring
If this is helpful, feel free to `Buy Me a Beer`; or check other options on the Github `❤️ Sponsor` link on the top of this page.


<a href="https://www.buymeacoffee.com/nitobuendia" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/arial-orange.png" alt="Buy Me A Coffee" style="height: 51px !important;width: 217px !important;" ></a>
