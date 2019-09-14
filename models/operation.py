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

  def __init__(self, timestamp: datetime.datetime, managed_asset: asset.Asset,
               operation_type: OperationType, quantity: int,
               price_per_unit: float, price_currency: Text):
    """Instantiates an operation.

    Args:
      timestamp: Date and time when operation was completed.
      managed_asset: Asset to operate.
      operation_type: Type of operation done.
      quantity: Quantity changed in the operation.
      price_per_unit: Price per each unit of the asset.
      price_currency: Currency in which price is expressed.
      operation_id: Id of the operation to create.
          Only to be used to load previous state.
    """
    self._id = str(uuid.uuid4())
    self.timestamp = timestamp
    self.managed_asset = managed_asset
    self.operation_type = operation_type
    self.quantity = quantity
    self.price_per_unit = price_per_unit
    self.price_currency = price_currency

  def __str__(self):
    """Converts operation to string."""
    return (
        'Operation<'
        f'id: {self._id}, '
        f'timestamp: {self.timestamp}, '
        f'operation_type: {self.operation_type}, '
        f'asset: {self.managed_asset}'
        f'quantity: {self.quantity}, '
        f'price: {self.price_currency} {self.price_per_unit}'
        '>'
    )

  def to_dict(self) -> Mapping:
    """Returns Dict represtation of Operation."""
    return {
        'operation_id': self._id,
        'timestamp': datetime.datetime.timestamp(self.timestamp),
        'asset': self.managed_asset.name,
        'operation_type': self.operation_type.value,
        'quantity': self.quantity,
        'price_per_unit': self.price_per_unit,
        'price_currency': self.price_currency,
    }

  def to_json(self):
    """Returns JSON representation of Operation."""
    return json.dumps(self.to_dict())
