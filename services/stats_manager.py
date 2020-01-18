"""Obtains and calculates stats and ratios of given assets."""

import enum
from models import asset
from models import portfolio
from models import stats
from services import asset_manager
from typing import Mapping
from yahoo_fin import stock_info


class StockAttribute(enum.Enum):
  """Yahoo Finance attribute names for stocks."""
  DEBT_TO_EQUITY = 'Total Debt/Equity (mrq)'
  DIVIDEND_YIELD = '5 Year Average Dividend Yield 4'
  EPS = 'Revenue Per Share (ttm)'
  PE = 'Trailing P/E'
  PROFIT_MARGIN = 'Profit Margin'
  RETURN_ON_EQUITY = 'Return on Equity (ttm)'
  REVENUE_GROWTH = 'Quarterly Revenue Growth (yoy)'
  VALUE_OVER_EBITDA = 'Enterprise Value/EBITDA 6'


def update_asset_stats(managed_asset: asset.Asset) -> stats.AssetStats:
  """Updates stats of given assets.

  Args:
    managed_asset: Asset for which to get stats.

  Returns:
    Stats of the given asset.
  """
  tracker = managed_asset.get_tracker()
  price = managed_asset.current_price

  if not tracker:
    return stats.StockStats(managed_asset=managed_asset, price=price)

  try:
    price = stock_info.get_live_price(tracker)
    managed_asset.current_price = price
  except Exception:
    return stats.StockStats(managed_asset=managed_asset, price=price)

  try:  # TODO: handle all types of assets instead of only stocks.
    stock_data = stock_info.get_stats(tracker)
    stock_stats = stats.StockStats(
        managed_asset=managed_asset,
        price=price,
        debt_to_equity=_get_stock_stat_value(
            stock_data, StockAttribute.DEBT_TO_EQUITY),
        dividend_yield=_get_stock_stat_value(
            stock_data, StockAttribute.DIVIDEND_YIELD),
        eps=_get_stock_stat_value(
            stock_data, StockAttribute.EPS),
        pe=_get_stock_stat_value(
            stock_data, StockAttribute.PE),
        profit_margin=_get_stock_stat_value(
            stock_data, StockAttribute.PROFIT_MARGIN),
        return_on_equity=_get_stock_stat_value(
            stock_data, StockAttribute.RETURN_ON_EQUITY),
        revenue_growth=_get_stock_stat_value(
            stock_data, StockAttribute.REVENUE_GROWTH),
        value_over_ebitda=_get_stock_stat_value(
            stock_data, StockAttribute.VALUE_OVER_EBITDA),
    )
    managed_asset.stats = stock_stats
    return stock_stats
  except Exception:
    return stats.StockStats(managed_asset=managed_asset, price=price)


def update_portfolio_stats(managed_portfolio: portfolio.Portfolio
                           ) -> Mapping[asset.Asset, stats.AssetStats]:
  """Updates the stats for all assets in the portfolio.

  Args:
    managed_portfolio: Portfolio from which to obtain stats.

  Returns:
    Map of asssets and their stats.
  """
  portfolio_assets = asset_manager.get_assets(managed_portfolio)
  portfolio_stats = {
      managed_asset: update_asset_stats(managed_asset)
      for managed_asset in portfolio_assets.values()
  }
  return portfolio_stats


def _get_stock_stat_value(stock_data, stock_attribute):
  """Gets the stock stat value from a given stock attribute.

  Args:
    stock: Stock information (pandas Dataframe).
    attribute_name: Attribute from which value is requested.

  Returns:
    Attribute value.
  """
  attribute = (
      stock_data.loc[stock_data['Attribute'] == stock_attribute.value])
  attribute_value = attribute['Value']

  try:
    attribute_series = attribute_value.values
  except Exception:
    print(stock_attribute.value, 'no values')
    return attribute_value

  if attribute_series:
    return _parse_and_format_value(attribute_series[0])
  else:
    print(stock_attribute.value, 'no item', attribute_series)
    return _parse_and_format_value('0')


def _parse_and_format_value(string_value):
  """Parses and formats a string into the stats format.

  Args:
    string_value: Value of the stat as string.

  Returns:
    Value of the stat as a float.
  """
  if str(string_value) == 'nan':
    return float(0)

  if type(string_value) == float:
    return string_value

  if type(string_value) == int:
    return float(string_value)

  if '%' in string_value:
    string_value = string_value.replace('%', '')
    return float(string_value) / 100

  return float(string_value)
