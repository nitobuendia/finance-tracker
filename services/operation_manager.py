"""Manages operations in a portfolio."""

import datetime
from models import portfolio
from models import operation
from services import asset_manager
from services import portfolio_manager
from typing import Text


def add_operation(
    managed_portfolio: portfolio.Portfolio, timestamp: datetime.datetime,
    asset_name: Text, operation_type: operation.OperationType,
    quantity: int, price_per_unit: float, price_currency: Text
) -> operation.Operation:
  """Creates a new operation within a porfolio.

    Args:
      managed_portfolio: Portfolio where operation was created.
      timestamp: Date and time when operation was completed.
      asset_name: Name of the asset to operate.
      operation_type: Type of operation done.
      quantity: Quantity changed in the operation.
      price_per_unit: Price per each unit of the asset.
          If interests or dividends, use dividend per share or equivalent per
          unit gain.
      price_currency: Currency in which price is expressed.
    """
  managed_asset = asset_manager.get_asset(managed_portfolio, asset_name)
  if not managed_asset:
    managed_asset = asset_manager.add_asset(managed_portfolio, asset_name)

  new_operation = operation.Operation(
      timestamp, managed_asset, operation_type, quantity, price_per_unit,
      price_currency)

  managed_portfolio.operations.append(new_operation)
  asset_manager.add_asset_operation(
      managed_portfolio, managed_asset, new_operation)

  portfolio_manager._store_portfolio(managed_portfolio)

  return new_operation


def get_changed_quantity(asset_operation: operation.Operation) -> int:
  """Gets the change in quantity for a given operation.

  Args:
    asset_operation: Operation from which to get change of quantity.

  Returns:
    Change of asset quantity for given operation.
  """
  if asset_operation.operation_type == operation.OperationType.BUY:
    return asset_operation.quantity
  elif asset_operation.operation_type == operation.OperationType.SELL:
    return -1 * asset_operation.quantity
  elif asset_operation.operation_type == operation.OperationType.DIVIDEND:
    return 0  # Dividends or interests do not change quantity position.


def get_changed_balance(asset_operation: operation.Operation) -> float:
  """Gets the change in balance for a given operation.

  Args:
    asset_operation: Operation from which to get change of balance.

  Returns:
    Change of asset balance for given operation.
  """
  # TODO: implement logic to convert currency of operation.
  if asset_operation.operation_type == operation.OperationType.BUY:
    return -1 * asset_operation.quantity * asset_operation.price_per_unit
  elif asset_operation.operation_type == operation.OperationType.SELL:
    return asset_operation.quantity * asset_operation.price_per_unit
  elif asset_operation.operation_type == operation.OperationType.DIVIDEND:
    # Dividens increase returns, without affecting quantity.
    return asset_operation.quantity * asset_operation.price_per_unit


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


def remove_operation(managed_portfolio: portfolio.Portfolio,
                     operation_to_remove: operation.Operation):
  """Removes an operation from a portfolio.

  Args:
    managed_portfolio: Portfolio from which to remove operation.
    operation_to_remove: Operation to remove.

  Raises:
    ValueError: Operation not found in portfolio.
  """
  if operation_to_remove not in managed_portfolio.operations:
    raise ValueError(
        f'{operation_to_remove} not found in {managed_portfolio}.')

  managed_portfolio.operations.remove(operation_to_remove)
  asset_manager.remove_asset_operation(
      managed_portfolio, managed_portfolio, operation_to_remove)

  portfolio_manager._store_portfolio(managed_portfolio)
