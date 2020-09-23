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


def get_asset_stats(managed_asset: asset.Asset) -> stats.AssetStats:
  """Gets the stats of a given asset.
  Args:
    managed_asset: Asset for which to get stats.

  Returns:
    Stats of the given asset.
  """
  if hasattr(managed_asset, 'stats') and managed_asset.stats:
    return managed_asset.stats

  return update_asset_stats(managed_asset)


def get_portfolio_stats(managed_portfolio: portfolio.Portfolio
                        ) -> Mapping[asset.Asset, stats.AssetStats]:
  """Gets the stats for all assets in the portfolio.

  Args:
    managed_portfolio: Portfolio from which to obtain stats.

  Returns:
    Map of asssets and their stats.
  """
  portfolio_assets = asset_manager.get_assets(managed_portfolio)
  portfolio_stats = {
      managed_asset: get_asset_stats(managed_asset)
      for managed_asset in portfolio_assets.values()
  }
  return portfolio_stats


def update_asset_stats(managed_asset: asset.Asset) -> stats.AssetStats:
  """Updates stats of given assets.

  Args:
    managed_asset: Asset for which to update stats.

  Returns:
    Stats of the given asset.
  """
  tracker = managed_asset.get_tracker()
  price = managed_asset.current_price

  if not tracker:
    return stats.StockStats(managed_asset=managed_asset, price=price)

  try:
    fetched_price = _parse_and_format_value(stock_info.get_live_price(tracker))
  except AssertionError:
    fetched_price = None

  if not fetched_price:
    print(f'{managed_asset.get_id()} price was not updated.')
    return stats.StockStats(managed_asset=managed_asset, price=price)

  price = fetched_price
  managed_asset.current_price = price

  try:
    stock_data = stock_info.get_stats(tracker)
  except Exception:
    print(f'Unable to update {managed_asset.get_id()} price.')
    return stats.StockStats(managed_asset=managed_asset, price=price)

  if stock_data.empty:
    return stats.StockStats(managed_asset=managed_asset, price=price)

  try:  # TODO: handle all types of assets instead of only stocks.
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
    print(f'{managed_asset.get_id()} financial metrics were not updated.')
    return stats.StockStats(managed_asset=managed_asset, price=price)


def update_portfolio_stats(managed_portfolio: portfolio.Portfolio
                           ) -> Mapping[asset.Asset, stats.AssetStats]:
  """Updates the stats for all assets in the portfolio.

  Args:
    managed_portfolio: Portfolio for which to update stats.

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
    stock: Stock information(pandas Dataframe).
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
    return attribute_value

  if attribute_series:
    return _parse_and_format_value(attribute_series[0])
  else:
    return _parse_and_format_value('0')


def _parse_and_format_value(string_value):
  """Parses and formats a string into the stats format.

  Args:
    string_value: Value of the stat as string.

  Returns:
    Value of the stat as a float.
  """
  if str(string_value).lower() == 'nan':
    return None

  if type(string_value) == float:
    return string_value

  if type(string_value) == int:
    return float(string_value)

  string_value = str(string_value)

  if '%' in string_value:
    string_value = string_value.replace('%', '')
    return float(string_value) / 100

  return float(string_value)
