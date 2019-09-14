"""Manages assets within a portfolio."""

from models import asset
from models import operation
from models import portfolio
from models import position
from services import operation_manager
from typing import Optional, Text


def add_asset(
        managed_portfolio: portfolio.Portfolio,
        asset_name: Text) -> asset.Asset:
  """Adds an asset to a given portfolio.

  Args:
    managed_portfolio: Portfolio where to add asset.
    asset_name: Name of the asset to add.

  Raises:
    ValueError: asset already exists in portfolio.

  Returns:
    New Asset created.
  """
  if asset_name in managed_portfolio.assets:
    raise ValueError('Asset already exists.')

  new_asset = asset.Asset(asset_name)
  managed_portfolio.assets[asset_name] = new_asset

  managed_portfolio.asset_positions[new_asset] = position.Position(
      managed_portfolio, new_asset, [], 0, 0.0)

  return new_asset


def get_asset(
        managed_portfolio: portfolio.Portfolio,
        asset_name: Text) -> Optional[asset.Asset]:
  """Gets an asset from a given portfolio.

    Args:
      managed_porfolio: Portfolio from which to get asset.
      asset_name: Name of the asset to retrieve.

    Returns:
      Asset if found. None if asset not existing.
    """
  return managed_portfolio.assets.get(asset_name)


def get_asset_position(managed_portfolio: portfolio.Portfolio,
                       managed_asset: asset.Asset) -> position.Position:
  """Gets the position of a given asset.

  Args:
    managed_portfolio: Portfolio where position exists.
    managed_asset: Asset for which to retrieve position.

  Raises:
    ValueError: Asset does not have a position in this portfolio.

  Returns:
    Position of the requested asset in the portfolio.
  """
  if managed_asset not in managed_portfolio.asset_positions:
    raise ValueError(
        f'{managed_asset} does not have a position in {managed_portfolio}.')

  return managed_portfolio.asset_positions[managed_asset]


def add_asset_operation(
        managed_portfolio: portfolio.Portfolio,
        managed_asset: asset.Asset, asset_operation: operation.Operation):
  """Adds a new operation to the asset and updates position.

  Args:
    managed_portfolio: Portfolio where asset operation happened.
    managed_asset: Asset for which operation happened.
    asset_operation: Operation was made.

  Raises:
    ValueError: asset quantity cannot be below 0.
  """
  asset_position = get_asset_position(managed_portfolio, managed_asset)
  quantity_change = operation_manager.get_changed_quantity(asset_operation)
  balance_change = operation_manager.get_changed_balance(asset_operation)

  if asset_position.quantity + quantity_change < 0:
    raise ValueError(f'{asset_operation} would make quantity negative.')

  asset_position.operations.append(asset_operation)
  asset_position.quantity += quantity_change
  asset_position.balance += balance_change


def remove_asset_operation(
        managed_portfolio: portfolio.Portfolio,
        managed_asset: asset.Asset, asset_operation: operation.Operation):
  """Removes an existing operation from the asset and updates position.

  Args:
    managed_portfolio: Portfolio where asset operation is undone.
    managed_asset: Asset for which operation is undone.
    asset_operation: Operation was undone.

  Raises:
    ValueError: operation does not exist for given asset and portfolio.
  """
  asset_position = get_asset_position(managed_portfolio, managed_asset)

  if asset_operation not in asset_position.operations:
    raise ValueError(f'{asset_operation} does not exist for {managed_asset}.')

  quantity_change = operation_manager.get_changed_quantity(asset_operation)
  balance_change = operation_manager.get_changed_balance(asset_operation)

  asset_position.operations.remove(asset_operation)
  asset_position.quantity -= quantity_change
  asset_position.balance -= balance_change
