import datetime
import json
import enum
import uuid
from models import asset
from typing import Mapping, Optional, Text


class OperationType(enum.Enum):
  """Types of supported operations."""
  BUY = 1
  SELL = 2
  DIVIDEND = 3  # Also applies for interest payment in simple operations.


class Operation(object):
  """Represents a financial or market operation on an asset."""

  def __init__(
          self, managed_asset: asset.Asset, timestamp: datetime.datetime,
          operation_type: OperationType, quantity: int, price_per_unit: float,
          operation_currency: Text):
    """Instantiates an operation.

    Args:
      managed_asset: Asset to operate.
      timestamp: Date and time when operation was completed.
      operation_type: Type of operation done.
      quantity: Quantity changed in the operation.
      price_per_unit: Price per each unit of the asset.
      operation_currency: Currency in which price is expressed.
    """
    self._id = str(uuid.uuid4())
    self.managed_asset = managed_asset
    self.timestamp = timestamp
    self.operation_type = operation_type
    self.quantity = quantity
    self.price_per_unit = price_per_unit
    self.operation_currency = operation_currency

  def __str__(self):
    """Converts operation to string."""
    return (
        'Operation<'
        f'id: {self._id}, '
        f'asset: {self.managed_asset.get_id()}'
        f'timestamp: {self.timestamp}, '
        f'operation_type: {self.operation_type}, '
        f'quantity: {self.quantity}, '
        f'price: {self.operation_currency} {self.price_per_unit}'
        '>'
    )

  def get_id(self):
    """Gets operation id."""
    return self._id

  def to_dict(self) -> Mapping:
    """Returns Dict represtation of Operation."""
    return {
        'operation_id': self._id,
        'timestamp': datetime.datetime.timestamp(self.timestamp),
        'asset': self.managed_asset.get_id(),
        'operation_type': self.operation_type.value,
        'quantity': self.quantity,
        'price_per_unit': self.price_per_unit,
        'operation_currency': self.operation_currency,
    }

  def to_json(self):
    """Returns JSON representation of Operation."""
    return json.dumps(self.to_dict())
