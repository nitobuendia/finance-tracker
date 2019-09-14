"""Manages assets within a portfolio."""

from models import asset
from models import operation
from models import portfolio
from models import position
from services import operation_manager
from services import portfolio_manager
from typing import Mapping, Optional, Sequence, Text


def add_asset(
        managed_portfolio: portfolio.Portfolio,
        asset_code: Text,
        asset_name: Text,
        asset_price: Optional[float] = 0.0,
        asset_currency: Optional[Text] = ''
) -> asset.Asset:
  """Adds an asset to a given portfolio.

  Args:
    managed_portfolio: Portfolio where to add asset.
    asset_code: Code of the asset to add.
    asset_name: Name of the asset to add.
    asset_price: Price of the asset.
    asset_currency: Currency of the asset price.

  Raises:
    ValueError: asset already exists in portfolio.

  Returns:
    New Asset created.
  """
  if contains_asset(managed_portfolio, asset_code):
    raise ValueError(f'Asset {asset_code} already exists.')

  new_asset = asset.Asset(asset_code, asset_name, asset_price, asset_currency)
  managed_portfolio.assets[asset_code] = new_asset
  portfolio_manager.store_portfolio(managed_portfolio)

  return new_asset


def add_operation(
        managed_asset: asset.Asset, asset_operation: operation.Operation):
  """Adds a new operation to the asset and updates position.

  Args:
    managed_asset: Asset for which operation happened.
    asset_operation: Operation was made.

  Raises:
    ValueError: operation already added to position.
  """
  asset_operations = get_operations(managed_asset)

  if asset_operation in asset_operations:
    raise ValueError(f'{asset_operation} already exists in {managed_asset}.')

  managed_asset.operations.append(asset_operation)


def contains_asset(
        managed_portfolio: portfolio.Portfolio, asset_code: Text) -> bool:
  """Returns whether a certain asset code exists in portfolio.

  Args:
    managed_portfolio: Portfolio where to search for asset.
    asset_code: Asset to check.

  Returns:
    Whether asset exists in current portfolio.
  """
  portfolio_assets = get_assets(managed_portfolio)
  return asset_code in portfolio_assets


def delete_operation(
        managed_asset: asset.Asset, asset_operation: operation.Operation):
  """Removes an existing operation from the asset and updates position.

  Args:
    managed_asset: Asset for which operation is undone.
    asset_operation: Operation was undone.

  Raises:
    ValueError: operation does not exist for given asset and portfolio.
  """
  asset_operations = get_operations(managed_asset)

  if asset_operation not in asset_operations:
    raise ValueError(f'{asset_operation} does not exist for {managed_asset}.')

  asset_operations.remove(asset_operation)


def get_asset(managed_portfolio: portfolio.Portfolio,
              asset_code: Text) -> asset.Asset:
  """Returns whether a certain asset code exists in portfolio.

  Args:
    managed_portfolio: Portfolio where to search for asset.
    asset_code: Asset to check.

  Raises:
    ValueError: asset_code not existing in portfolio.

  Returns:
    Whether asset exists in current portfolio.
  """
  if not contains_asset(managed_portfolio, asset_code):
    raise ValueError(
        f'{ asset_code } does not exist in { managed_portfolio }')

  portfolio_assets = get_assets(managed_portfolio)
  return portfolio_assets[asset_code]


def get_assets(
        managed_portfolio: portfolio.Portfolio) -> Mapping[Text, asset.Asset]:
  """Gets all the assets in the portfolio.

  Args:
    managed_portfolio: Portfolio from which to obtain assets.

  Returns:
    Map of asset to its ids.
  """
  return managed_portfolio.assets


def get_operations(
        managed_asset: asset.Asset) -> Sequence[operation.Operation]:
  """Gets operations for a given asset.

  Args:
    managed_asset: Asset for which to retrieve operations.

  Returns:
    List of operations done in given asset.
  """
  return managed_asset.operations
