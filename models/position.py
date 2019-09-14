import json
from models import asset
from models import operation
from models import portfolio
from typing import Mapping, Sequence, Text


class Position(object):
  """Represents a financial position in a given asset."""

  def __init__(self, managed_portfolio: portfolio.Portfolio,
               managed_asset: asset.Asset,
               asset_operations: Sequence[operation.Operation],
               asset_quantity: int, asset_balance: float):
    """Instantiates an asset position.

    Args:
      managed_portfolio: Portfolio where position exists.
      managed_asset: Asset whose position is represented.
      asset_operations: List of operations for given asset.
      asset_quantity: Quantity of the asset remaining.
      asset_balance: Final value of the asset.
    """
    self.portfolio = managed_portfolio
    self.asset = managed_asset
    self.operations = asset_operations
    self.quantity = asset_quantity
    self.balance = asset_balance

  def to_dict(self) -> Mapping:
    """Returns Dict represtation of Position."""
    return {
        'portfolio_id': self.portfolio.get_id(),
        'asset': self.asset.name,
        'quantity': self.quantity,
        'balance': self.balance,
    }

  def to_json(self) -> Text:
    """Returns JSON representation of Position."""
    return json.dumps(self.to_dict())
