"""Calculates positions of given assets."""

import enum

from models import asset
from models import operation
from models import portfolio
from models import position
from services import asset_manager
from typing import Iterable, Mapping, Tuple, Union

Number = Union[int, float]
OperationIterable = Iterable[operation.Operation]
OperationType = operation.OperationType  # Shorthand as it's used a lot.
OperationsByType = Mapping[OperationType, OperationIterable]
TypeCalculation = Mapping[OperationType, Number]


class ValuationMethod(enum.Enum):
  """Asset valuation method for calculating asset returns."""
  UNKNOWN = 'Unknown'
  FIFO = 'FIFO'
  LIFO = 'LIFO'
  AVERAGE = 'Average Price'


class OperationForCalculation(operation.Operation):
  """A copy of an operation to be used for calculations."""

  def __init__(self, original_operation: operation.Operation):
    """Initializes Operation for Calculation.

    Args:
      original_operation: Operation to copy.
    """
    self.timestamp = original_operation.timestamp
    self.quantity = original_operation.quantity
    self.remaining_quantity = original_operation.quantity
    self.price_per_unit = original_operation.price_per_unit
    self.operation_currency = original_operation.operation_currency

  def __str__(self):
    """Converts operation to string."""
    return (
        'OperationForCalculation<'
        f'timestamp: {self.timestamp}, '
        f'quantity: {self.quantity}, '
        f'remaining_quantity: {self.remaining_quantity}, '
        f'price: {self.operation_currency} {self.price_per_unit}'
        '>'
    )


def get_position(
        managed_asset: asset.Asset,
        valuation_method: ValuationMethod = ValuationMethod.FIFO
) -> position.Position:
  """Gets position of given asset.

  Args:
    managed_asset: Asset for which to calculate position.
    valuation_method: Inventory valuation method to calculate returns.

  Raises:
    NotImplementedError: When valuation method has not been implemented.

  Returns:
    Position of the given asset.
  """
  if valuation_method == ValuationMethod.AVERAGE:
    return _get_position_by_average(managed_asset)
  elif valuation_method == ValuationMethod.FIFO:
    return _get_position_by_fifo(managed_asset)
  elif valuation_method == ValuationMethod.LIFO:
    pass
    # TODO: return _get_position_by_lifo(managed_asset)

  raise NotImplementedError(
      f'Valuation method {valuation_method.value} not implemented.')


def get_positions(
    managed_portfolio: portfolio.Portfolio,
    valuation_method: ValuationMethod = ValuationMethod.FIFO
) -> Mapping[asset.Asset, position.Position]:
  """Gets the position of all assets in the portfolio.

  Args:
    managed_portfolio: Portfolio from which to obtain position.
    valuation_method: Inventory valuation method to calculate returns.

  Returns:
    Map of assets and their current positions.
  """
  portfolio_assets = asset_manager.get_assets(managed_portfolio)
  portfolio_positions = {
      managed_asset: get_position(managed_asset, valuation_method)
      for managed_asset in portfolio_assets.values()
  }
  return portfolio_positions


# FIFO calculations.
def _get_position_by_fifo(managed_asset: asset.Asset) -> position.Position:
  """Gets position of given asset following Fist In, First Out method.

  First In, First Out(FIFO) methodology assumes that the sold assets are the
  first acquired ones.

  Args:
    managed_asset: Asset for which to calculate positions.

  Returns:
    Position of the asset by FIFO methodology.
  """
  current_price = managed_asset.current_price

  asset_operations = list(asset_manager.get_operations(managed_asset).values())
  asset_operations.sort(key=lambda op: op.timestamp)
  operations_by_type = _get_operations_by_type(asset_operations)

  sold_units = _get_fifo_sold_units(operations_by_type)
  buy_units_sold, buy_units_unsold = (
      _get_fifo_buy_units_sold(operations_by_type))
  rebought_units, sold_rebought_units, sold_not_rebought_units = (
      _get_fifo_rebought_units_sold(operations_by_type))

  remaining_quantity = _get_total_quantity(buy_units_unsold)
  market_value = remaining_quantity * current_price

  realized_pl, realized_roi = (
      _get_realized_pl_and_roi(buy_units_sold, sold_units))

  unrealized_pl, unrealized_roi = _get_unrealized_pl_and_roi(
      buy_units_unsold, managed_asset.current_price)

  opportunity_pl, opportunity_roi = _get_opportunity_pl_and_roi(
      sold_not_rebought_units, sold_rebought_units, rebought_units,
      current_price)

  dividend_value, dividend_yield = (
      _get_dividend_value_and_yield(operations_by_type))

  return position.Position(
      managed_asset, remaining_quantity, market_value,
      realized_pl, realized_roi, unrealized_pl, unrealized_roi,
      opportunity_pl, opportunity_roi, dividend_value, dividend_yield)


def _get_fifo_sold_units(
        operations_by_type: OperationsByType) -> OperationIterable:
  """Gets list of operations that were sold using FIFO method.

  Args:
    operations_by_type: Operations by type.

  Returns:
    List of sell operations by FIFO method.
  """
  return _copy_list_of_operations_for_calculation(
      operations_by_type[OperationType.SELL])


def _get_fifo_buy_units_sold(
    operations_by_type: OperationsByType
) -> Tuple[OperationIterable, OperationIterable]:
  """Gets list of buy operations that were sold using FIFO method.

  Args:
    operations_by_type: Operations by type.

  Raises:
    ValueError: sold more units than we had bought.

  Returns:
    List of operations split by whether they were sold or not.
  """
  sell_operations = operations_by_type[OperationType.SELL]
  buy_operations = operations_by_type[OperationType.BUY]

  if not sell_operations:
    return ([], buy_operations)

  if not buy_operations:
    raise ValueError('No buy operations found. Overselling asset.')

  buy_operations = _copy_list_of_operations_for_calculation(buy_operations)

  # TODO: an improvement here would be to iterate the list of sell instead of
  # the total value. This would allow to verify that the sell timestamp was
  # after a buy timestamp. Otherwise, we sold more asset units than we had.
  sell_operations = _copy_list_of_operations_for_calculation(sell_operations)
  sell_quantity = _get_total_quantity(sell_operations)

  buy_units_sold = []
  buy_units_unsold = []
  buy_units_quantity = 0

  while buy_units_quantity < sell_quantity:
    next_buy_operation = buy_operations.pop(0)
    if buy_units_quantity + next_buy_operation.quantity <= sell_quantity:
      buy_units_sold.append(OperationForCalculation(next_buy_operation))
      buy_units_quantity += next_buy_operation.quantity
    else:  # Last unit.
      remaining_units = sell_quantity - buy_units_quantity
      buy_units_quantity += remaining_units

      partial_buy_sold = OperationForCalculation(next_buy_operation)
      partial_buy_sold.quantity = remaining_units
      buy_units_sold.append(OperationForCalculation(partial_buy_sold))

      partial_buy_unsold = OperationForCalculation(next_buy_operation)
      partial_buy_unsold.quantity -= remaining_units
      buy_units_unsold.append(OperationForCalculation(partial_buy_unsold))

  buy_units_unsold.extend(buy_operations)

  return (buy_units_sold, buy_units_unsold)


def _get_fifo_rebought_units_sold(
    operations_by_type: OperationsByType
) -> Tuple[OperationIterable, OperationIterable, OperationIterable]:
  """Gets list of buy units that were rebought after sell using FIFO method.

  Args:
    operations_by_type: Operations by type.

  Returns:
    Tuple containing:
      List of buy operations that were rebought.
      List of sell operations that were not rebought.
  """
  sell_operations = operations_by_type[OperationType.SELL]
  if not sell_operations:
    return ([], [], [])

  sell_operations = _copy_list_of_operations_for_calculation(sell_operations)
  _, buy_units_unsold = _get_fifo_buy_units_sold(operations_by_type)

  sold_rebought_units = []
  sold_not_rebought_units = []
  rebought_units = []

  next_sell = None
  next_buy = None

  # TODO: improve logic to consider timestamps. At the moment, FIFO is in
  # absolute time. This means that a unit could be considered rebought even if
  # the sale for that unit happened at a later date.
  while sell_operations and buy_units_unsold:
    next_sell = next_sell or sell_operations.pop(0)
    next_buy = next_buy or buy_units_unsold.pop(0)

    if next_sell.remaining_quantity == next_buy.remaining_quantity:
      sold_rebought_units.append(OperationForCalculation(next_sell))
      rebought_units.append(OperationForCalculation(next_buy))
      next_sell = None
      next_buy = None

    elif next_sell.remaining_quantity > next_buy.remaining_quantity:
      next_sell.remaining_quantity -= next_buy.remaining_quantity
      rebought_units.append(OperationForCalculation(next_buy))
      next_buy = None

    elif next_sell.remaining_quantity < next_buy.remaining_quantity:
      sold_rebought_units.append(OperationForCalculation(next_sell))
      next_buy.remaining_quantity -= next_sell.remaining_quantity
      next_sell = None

  if next_sell:
    partial_sell_rebought = OperationForCalculation(next_sell)
    partial_sell_rebought.quantity -= next_sell.remaining_quantity
    sold_rebought_units.append(OperationForCalculation(partial_sell_rebought))

    partial_sell_not_rebought = OperationForCalculation(next_sell)
    partial_sell_not_rebought.quantity = next_sell.remaining_quantity
    sold_not_rebought_units.append(
        OperationForCalculation(partial_sell_not_rebought))

  if next_buy:
    partial_rebought = OperationForCalculation(next_buy)
    partial_rebought.quantity -= next_buy.remaining_quantity
    rebought_units.append(OperationForCalculation(partial_rebought))
    # We do not care about buys which are new (not rebought).

  return (rebought_units, sold_rebought_units, sold_not_rebought_units)


# TODO: LIFO calculations.
def _get_position_by_lifo(managed_asset: asset.Asset) -> position.Position:
  """Gets position of given asset following Last In, First Out method.

  Last In, First Out (LIFO) methodology assumes that the sold assets will be
  the last acquired ones.

  Args:
    managed_asset: Asset for which to calculate positions.

  Returns:
    Position of the asset by LIFO methodology.
  """
  remaining_quantity = 0
  market_value = 0

  realized_pl = 0
  realized_roi = 0

  unrealized_pl = 0
  unrealized_roi = 0

  opportunity_pl = 0
  opportunity_roi = 0

  unrealized_pl = 0
  unrealized_roi = 0

  dividend_value = 0
  dividend_yield = 0

  return position.Position(
      managed_asset, remaining_quantity, market_value,
      realized_pl, realized_roi, unrealized_pl, unrealized_roi,
      opportunity_pl, opportunity_roi, dividend_value, dividend_yield)


# Average position calculations.
def _get_position_by_average(managed_asset: asset.Asset) -> position.Position:
  """Gets position of given asset applying average prices.

  Average prices does not take into consideration when buy/sell positions where
  done. As such, it is error prone. As assets bought at later time may distort
  the return on investment that were realized. However, it is the simplest
  method to calculate.

  Args:
    managed_asset: Asset for which to calculate positions.

  Returns:
    Position of the asset by average methodology.
  """
  current_price = managed_asset.current_price

  asset_operations = list(asset_manager.get_operations(managed_asset).values())
  operations_by_type = _get_operations_by_type(asset_operations)

  sold_units = operations_by_type[OperationType.SELL]

  buy_units_sold, buy_units_unsold = (
      _get_average_buy_units_sold(operations_by_type))

  rebought_units, sold_rebought_units, sold_not_rebought_units = (
      _get_average_rebought_units_sold(operations_by_type))

  remaining_quantity = _get_total_quantity(buy_units_unsold)
  market_value = remaining_quantity * current_price

  realized_pl, realized_roi = (
      _get_realized_pl_and_roi(buy_units_sold, sold_units))

  unrealized_pl, unrealized_roi = _get_unrealized_pl_and_roi(
      buy_units_unsold, managed_asset.current_price)

  opportunity_pl, opportunity_roi = _get_opportunity_pl_and_roi(
      sold_not_rebought_units, sold_rebought_units, rebought_units,
      current_price)

  dividend_value, dividend_yield = (
      _get_dividend_value_and_yield(operations_by_type))

  return position.Position(
      managed_asset, remaining_quantity, market_value,
      realized_pl, realized_roi, unrealized_pl, unrealized_roi,
      opportunity_pl, opportunity_roi, dividend_value, dividend_yield)


def _get_average_buy_units_sold(
    operations_by_type: OperationsByType
) -> Tuple[OperationIterable, OperationIterable]:
  """Gets list of operations that were sold using average method.

  Args:
    operations_by_type: Operations by type.

  Raises:
    ValueError: sold more units than we had bought.

  Returns:
    List of operations split by whether they were sold or not.
  """
  sell_operations = operations_by_type[OperationType.SELL]
  buy_operations = operations_by_type[OperationType.BUY]

  if not sell_operations:
    return ([], buy_operations)

  if not buy_operations:
    raise ValueError('No buy operations found. Overselling asset.')

  buy_operations = _copy_list_of_operations_for_calculation(buy_operations)
  average_price = _get_average_value_by_type(operations_by_type)

  sell_operations = _copy_list_of_operations_for_calculation(sell_operations)
  sell_quantity = _get_total_quantity(sell_operations)

  buy_units_sold = []
  buy_units_unsold = []
  buy_units_quantity = 0

  while buy_units_quantity < sell_quantity:
    next_buy_operation = buy_operations.pop(0)
    next_buy_operation.price_per_unit = average_price[OperationType.BUY]
    if buy_units_quantity + next_buy_operation.quantity <= sell_quantity:
      buy_units_sold.append(OperationForCalculation(next_buy_operation))
      buy_units_quantity += next_buy_operation.quantity
    else:  # Last unit.
      remaining_units = sell_quantity - buy_units_quantity
      buy_units_quantity += remaining_units

      partial_buy_sold = OperationForCalculation(next_buy_operation)
      partial_buy_sold.quantity = remaining_units
      buy_units_sold.append(OperationForCalculation(partial_buy_sold))

      partial_buy_unsold = OperationForCalculation(next_buy_operation)
      partial_buy_unsold.quantity -= remaining_units
      buy_units_unsold.append(OperationForCalculation(partial_buy_unsold))

  buy_units_unsold.extend(buy_operations)

  return (buy_units_sold, buy_units_unsold)


def _get_average_rebought_units_sold(
    operations_by_type: OperationsByType
) -> Tuple[OperationIterable, OperationIterable, OperationIterable]:
  """Gets list of buy units that were rebought after sell using average method.

  Args:
    operations_by_type: Operations by type.

  Returns:
    Tuple containing:
      List of buy operations that were rebought.
      List of sell operations that were not rebought.
  """
  sell_operations = operations_by_type[OperationType.SELL]
  if not sell_operations:
    return ([], [], [])

  average_price = _get_average_value_by_type(operations_by_type)
  average_buy_price = average_price[OperationType.BUY]
  average_sell_price = average_price[OperationType.SELL]

  sell_operations = _copy_list_of_operations_for_calculation(sell_operations)
  for sell_op in sell_operations:
    sell_op.price_per_unit = average_sell_price

  _, buy_units_unsold = _get_average_buy_units_sold(operations_by_type)
  for buy_op in buy_units_unsold:
    buy_op.price_per_unit = average_buy_price

  sold_rebought_units = []
  sold_not_rebought_units = []
  rebought_units = []

  next_sell = None
  next_buy = None

  while sell_operations and buy_units_unsold:
    next_sell = next_sell or sell_operations.pop(0)
    next_buy = next_buy or buy_units_unsold.pop(0)

    if next_sell.remaining_quantity == next_buy.remaining_quantity:
      sold_rebought_units.append(OperationForCalculation(next_sell))
      rebought_units.append(OperationForCalculation(next_buy))
      next_sell = None
      next_buy = None

    elif next_sell.remaining_quantity > next_buy.remaining_quantity:
      next_sell.remaining_quantity -= next_buy.remaining_quantity
      rebought_units.append(OperationForCalculation(next_buy))
      next_buy = None

    elif next_sell.remaining_quantity < next_buy.remaining_quantity:
      sold_rebought_units.append(OperationForCalculation(next_sell))
      next_buy.remaining_quantity -= next_sell.remaining_quantity
      next_sell = None

  if next_sell:
    partial_sell_rebought = OperationForCalculation(next_sell)
    partial_sell_rebought.quantity -= next_sell.remaining_quantity
    sold_rebought_units.append(OperationForCalculation(partial_sell_rebought))

    partial_sell_not_rebought = OperationForCalculation(next_sell)
    partial_sell_rebought.quantity = next_sell.remaining_quantity
    sold_not_rebought_units.append(
        OperationForCalculation(partial_sell_not_rebought))

  if next_buy:
    partial_rebought = OperationForCalculation(next_buy)
    partial_rebought.quantity -= next_buy.remaining_quantity
    rebought_units.append(OperationForCalculation(partial_rebought))
    # We do not care about buys which are new (not rebought).

  return (rebought_units, sold_rebought_units, sold_not_rebought_units)


# Helper functions.
def _get_operations_by_type(
        asset_operations: OperationIterable) -> OperationsByType:
  """Splits all operations into each type.

  Args:
    asset_operations: Asset operations to classify.

  Returns:
    Operations classified by type.
  """
  return {
      operation_type: _get_operation_type_for_calculation(
          asset_operations, operation_type)
      for operation_type in OperationType
  }


def _copy_list_of_operations_for_calculation(
        operation_list: OperationIterable) -> OperationIterable:
  """Copies a list of operations for calculations.

  Args:
    operation_list: List of operations to copy.

  Returns:
    List of operations copy.
  """
  return [OperationForCalculation(op) for op in operation_list]


def _get_operation_type_for_calculation(
        asset_operations: OperationIterable,
        operation_type: OperationType
) -> OperationIterable:
  """Gets all operations of a given type from the list for calculations.

  It does not change order. As such, it can be used within both LIFO and FIFO
  method without alterations.

  Args:
    asset_operations: List of operations for given asset.
    operation_type: Type of operation for which to filter.

  Returns:
    List of operations for calculations of the given type.
  """
  return [
      OperationForCalculation(op)
      for op in asset_operations
      if op.operation_type == operation_type
  ]


def _get_total_quantity(operation_list: OperationIterable) -> int:
  """Calculates the total quantity of a given operation list.

  Args:
    operation_list: Operations for which to calculate total quantity.

  Returns:
    Total quantity.
  """
  return sum([op.quantity for op in operation_list])


def _get_total_quantity_by_type(
        operations_by_type: OperationsByType) -> TypeCalculation:
  """Calculates total assets in each operation type.

  Args:
    operations_by_type: List of operations by type.

  Returns:
    Total quantity of assets for each operation type.
  """
  return {
      operation_type: _get_total_quantity(operation_list)
      for operation_type, operation_list in operations_by_type.items()
  }


def _get_total_value(operation_list: OperationIterable) -> float:
  """Calculates the total value of a given operation list.

  Args:
    operation_list: Operations for which to calculate total value.

  Returns:
    Total value.
  """
  return sum([op.quantity * op.price_per_unit for op in operation_list])


def _get_total_value_by_type(
        operations_by_type: OperationsByType) -> TypeCalculation:
  """Calculates total assets in each operation type.

  Args:
    operations_by_type: List of operations by type.

  Returns:
    Total value of assets for each operation type.
  """
  return {
      operation_type: _get_total_value(operation_list)
      for operation_type, operation_list in operations_by_type.items()
  }


def _get_weighted_average_value(operation_list: OperationIterable) -> float:
  """Calculates the average weighted value of a given operation list.

  Args:
    operation_list: Operations for which to calculate weighted average value.

  Returns:
    Weighted average value.
  """
  total_value = _get_total_value(operation_list)
  total_quantity = _get_total_quantity(operation_list)
  return total_value / total_quantity


def _get_average_value_by_type(
        operations_by_type: OperationsByType) -> TypeCalculation:
  """Calculates average asset value in each operation type.

  Args:
    operations_by_type: List of operations by type.

  Returns:
    Average value of assets for each operation type.
  """
  return {
      operation_type: _get_weighted_average_value(operation_list)
      for operation_type, operation_list in operations_by_type.items()
  }


def _get_realized_pl_and_roi(
        buy_units_sold: OperationIterable,
        sold_units: OperationIterable) -> Tuple[float, float]:
  """Calculates the realized profit and loss based on units sold.

  Args:
    buy_units_sold: List of buy operations of assets sold.
    sold_units: List of sell operations.

  Returns:
    Realized profit and loss, and return on investment.
  """
  total_sold_value = _get_total_value(sold_units)
  total_buy_sold_value = _get_total_value(buy_units_sold)

  realized_pl = total_sold_value - total_buy_sold_value
  realized_roi = (
      realized_pl / total_buy_sold_value
      if total_buy_sold_value > 0 else 0)

  return (realized_pl, realized_roi)


def _get_unrealized_pl_and_roi(
        buy_units_unsold: OperationIterable,
        current_price: float) -> Tuple[float, float]:
  """Calculates the unrealized profit and loss based on units unsold.

  Args:
    buy_units_unsold: List of buy operations of assets not yet sold.
    current_price: Current price of asset.

  Returns:
    Unrealized profit and loss, and return on investment.
  """
  total_buy_unsold_value = _get_total_value(buy_units_unsold)
  total_buy_unsold_quantity = _get_total_quantity(buy_units_unsold)
  current_value_of_unsold = total_buy_unsold_quantity * current_price

  unrealized_pl = current_value_of_unsold - total_buy_unsold_value
  unrealized_roi = (
      unrealized_pl / total_buy_unsold_value
      if total_buy_unsold_value > 0 else 0)

  return (unrealized_pl, unrealized_roi)


def _get_opportunity_pl_and_roi(
        sold_not_rebought_units: OperationIterable,
        sold_rebought_units: OperationIterable,
        rebought_units: OperationIterable,
        current_price: float) -> Tuple[float, float]:
  """Calculates the opportunity profit and loss.

  Args:
    sold_units: List of sell operations which remains sold.
    sold_rebought_units: List of sell operations which were rebought.
    rebought_units: List of buy operations of assets rebought.
    current_price: Current price of asset.

  Returns:
    Opportunity profit and loss, and return on investment.
  """
  # Profit/Loss of opportunity of buying the assets today.
  sold_quantity = _get_total_quantity(sold_not_rebought_units)
  sold_value = _get_total_value(sold_not_rebought_units)
  sold_current_value = sold_quantity * current_price

  opportunity_pl_rebuy = sold_value - sold_current_value

  # Profit/Loss of re-buying assets bought after sell.
  rebought_sell_value = _get_total_value(sold_rebought_units)
  rebought_buy_value = _get_total_value(rebought_units)

  realized_pl_rebought = rebought_sell_value - rebought_buy_value

  # Total opportunity and ROI.
  total_sold_value = sold_value + rebought_sell_value
  opportunity_pl = opportunity_pl_rebuy + realized_pl_rebought
  opportunity_roi = (
      opportunity_pl / total_sold_value if total_sold_value > 0 else 0)

  return (opportunity_pl, opportunity_roi)


def _get_dividend_value_and_yield(
    operations_by_type: OperationsByType
) -> Tuple[float, float]:
  """Calculates dividend value and yield.

  At the moment, this only works with average price yield, which is not a very
  accurate method. Read TODO to know what else needs to be done here.

  Args:
    operations_by_type: Operations by type.

  Returns:
    Total dividend value and yield.
  """
  # TODO: calculating dividend yield accurately requires calculating the market
  # value at any given timestamp to calculate dividends per share and price.
  # First, this would require a new methodology to calculate positions for each
  # dividend operation timestamp. This has not been added yet.
  # Second, this would require historical prices, of which the current system
  # is not keeping track. A workaround is to compare against the buy prices,
  # which is not the actual financial metric definition, but does provide a
  # sense of return of investments. This is the current logic.
  dividend_value = _get_total_value(operations_by_type[OperationType.DIVIDEND])
  dividend_quantity = (
      _get_total_quantity(operations_by_type[OperationType.DIVIDEND]))

  dividend_per_share = (
      dividend_value / dividend_quantity if dividend_quantity > 0 else 0)

  buy_average = (
      _get_weighted_average_value(operations_by_type[OperationType.BUY]))

  dividend_yield = dividend_per_share / buy_average if buy_average > 0 else 0

  return (dividend_value, dividend_yield)
