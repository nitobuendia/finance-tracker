"""Manages operations in a portfolio."""

import datetime
import itertools
from models import asset
from models import portfolio
from models import operation
from services import asset_manager
from services import portfolio_manager
from typing import Optional, Sequence, Text


def add_operation(
    managed_portfolio: portfolio.Portfolio,
    managed_asset: asset.Asset,
    timestamp: datetime.datetime,
    operation_type: operation.OperationType,
    quantity: int, price_per_unit: float,
    operation_currency: Optional[Text] = ''
) -> operation.Operation:
  """Creates a new operation within a porfolio.

    Args:
      managed_portfolio: Portfolio where operation was created.
      managed_asset: Asset to operate.
      timestamp: Date and time when operation was completed.
      operation_type: Type of operation done.
      quantity: Quantity changed in the operation.
      price_per_unit: Price per each unit of the asset.
          If interests or dividends, use dividend per share or equivalent per
          unit gain.
      operation_currency: Currency in which price is expressed.
    """
  operation_currency = operation_currency or managed_portfolio.currency

  new_operation = operation.Operation(
      managed_asset, timestamp, operation_type, quantity, price_per_unit,
      operation_currency)

  asset_manager.add_operation(managed_asset, new_operation)
  portfolio_manager.store_portfolio(managed_portfolio)

  return new_operation


def delete_operation(managed_portfolio: portfolio.Portfolio,
                     operation_to_remove: operation.Operation):
  """Removes an operation from a portfolio.

  Args:
    managed_portfolio: Portfolio from which to remove operation.
    operation_to_remove: Operation to remove.

  Raises:
    ValueError: Operation not found in portfolio.
  """
  managed_asset = operation_to_remove.managed_asset

  if operation_to_remove not in managed_asset.operations:
    raise ValueError(
        f'{operation_to_remove} not found in {managed_asset}.')

  asset_manager.delete_operation(managed_asset, operation_to_remove)
  portfolio_manager.store_portfolio(managed_portfolio)


def get_operation_type(operation_type_name: Text) -> operation.OperationType:
  """Gets an operation type based on name.

  Args:
    operation_type_name: Name of the type of operation.

  Returns:
    Name of the operation.
  """
  if operation_type_name.upper() == 'BUY':
    return operation.OperationType.BUY
  elif operation_type_name.upper() == 'SELL':
    return operation.OperationType.SELL
  elif operation_type_name.upper() == 'DIVIDEND':
    return operation.OperationType.DIVIDEND
  else:
    raise ValueError(f'Unknown operation type: {operation_type_name}.')


def get_operations(managed_portfolio: portfolio.Portfolio
                   ) -> Sequence[operation.Operation]:
  """Gets all the position of all assets in the portfolio.

  Args:
    managed_portfolio: Portfolio from which to obtain operations.

  Returns:
    List of all portfolio operations.
  """
  managed_assets = asset_manager.get_assets(managed_portfolio)
  portfolio_operations = list(itertools.chain.from_iterable([
      managed_asset.operations for managed_asset in managed_assets.values()
  ]))
  portfolio_operations.sort(key=lambda x: x.timestamp)
  return portfolio_operations
