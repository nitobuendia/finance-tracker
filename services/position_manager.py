"""Calculates positions of given assets."""

from models import asset
from models import operation
from models import portfolio
from models import position
from services import asset_manager
from typing import Mapping


def get_position(managed_asset: asset.Asset) -> position.Position:
  """Gets position of given asset.

  Args:
    managed_asset: Asset for which to calculate position.

  Returns:
    Position of the given asset.
  """
  buy_type = operation.OperationType.BUY
  sell_type = operation.OperationType.SELL
  dividend_type = operation.OperationType.DIVIDEND

  total_quantity = {
      buy_type: 0,
      sell_type: 0,
      dividend_type: 0,
  }
  total_value = {
      buy_type: 0,
      sell_type: 0,
      dividend_type: 0,
  }
  asset_operations = asset_manager.get_operations(managed_asset)
  for asset_operation in asset_operations.values():
    # TODO: add currency conversion.
    total_quantity[asset_operation.operation_type] += asset_operation.quantity
    total_value[asset_operation.operation_type] += (
        asset_operation.quantity * asset_operation.price_per_unit)

  # TODO: change average to FIFO methodology.
  average_price = {
      buy_type: (
          total_value[buy_type] / total_quantity[buy_type]
          if total_quantity[buy_type] > 0 else 0
      ),
      sell_type: (
          total_value[sell_type] / total_quantity[sell_type]
          if total_quantity[sell_type] > 0 else 0
      ),
      dividend_type: (
          total_value[dividend_type] / total_quantity[dividend_type]
          if total_quantity[dividend_type] > 0 else 0
      ),
  }

  cost_of_sold_units = total_quantity[sell_type] * average_price[buy_type]
  realized_pl = total_value[sell_type] - cost_of_sold_units
  realized_roi = (realized_pl / cost_of_sold_units
                  if cost_of_sold_units > 0 else 0)

  remaining_quantity = total_quantity[buy_type] - total_quantity[sell_type]
  market_value = remaining_quantity * managed_asset.current_price
  cost_of_remaining_units = remaining_quantity * average_price[buy_type]
  unrealized_pl = market_value - cost_of_remaining_units
  unrealized_roi = (unrealized_pl / cost_of_remaining_units
                    if cost_of_remaining_units > 0 else 0)

  current_value_of_sold_units = (
      total_quantity[sell_type] * managed_asset.current_price)
  opportunity_pl = total_value[sell_type] - current_value_of_sold_units
  opportunity_roi = (opportunity_pl / total_value[sell_type]
                     if total_value[sell_type] > 0 else 0)

  dividends = total_value[dividend_type]
  dividend_per_share = (dividends / total_quantity[dividend_type]
                        if total_quantity[dividend_type] > 0 else 0)
  dividend_yield = (dividend_per_share / average_price[buy_type]
                    if average_price[buy_type] > 0 else 0)

  return position.Position(
      managed_asset, remaining_quantity, market_value,
      realized_pl, realized_roi, unrealized_pl, unrealized_roi,
      opportunity_pl, opportunity_roi, dividends, dividend_yield)


def get_positions(managed_portfolio: portfolio.Portfolio
                  ) -> Mapping[asset.Asset, position.Position]:
  """Gets the position of all assets in the portfolio.

  Args:
    managed_portfolio: Portfolio from which to obtain position.

  Returns:
    Map of assets and their current positions.
  """
  portfolio_assets = asset_manager.get_assets(managed_portfolio)
  portfolio_positions = {
      managed_asset: get_position(managed_asset)
      for managed_asset in portfolio_assets.values()
  }
  return portfolio_positions
