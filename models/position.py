import json
from models import asset
from models import operation
from models import portfolio
from typing import Mapping, Sequence, Text


class Position(object):
  """Represents a financial position in a given asset."""

  def __init__(self,
               managed_asset: asset.Asset,
               quantity: int,
               market_value: float,
               realized_pl: float,
               realized_roi: float,
               unrealized_pl: float,
               unrealized_roi: float,
               dividends: float,
               dividend_yield: float):
    """Instantiates an asset position.

    Args:
      managed_asset: Asset whose position is represented.
      quantity: Quantity of the asset held.
      market_value: Current value of the position.
      realized_pl: Profit/Loss already realized.
      realized_roi: ROI of alreadt realized transactions.
      unrealized_pl: Potential Profit/Loss.
      unrealized_roi: Potential ROI of unrealized operation.
      dividends: Total dividends received.
      dividend_yield: Average dividend yield received.
    """
    self.asset = managed_asset
    self.quantity = quantity
    self.market_value = market_value
    self.realized_pl = realized_pl
    self.realized_roi = realized_roi
    self.unrealized_pl = unrealized_pl
    self.unrealized_roi = unrealized_roi
    self.dividends = dividends
    self.dividend_yield = dividend_yield

  def to_dict(self) -> Mapping:
    """Returns Dict represtation of Position."""
    return {
        'asset': self.asset.get_id(),
        'positquantityion': self.quantity,
        'market_value': self.market_value,
        'realized_pl': self.realized_pl,
        'realized_roi': self.realized_roi,
        'unrealized_pl': self.unrealized_pl,
        'unrealized_roi': self.unrealized_roi,
        'dividends': self.dividends,
        'dividend_yield': self.dividend_yield,
    }

  def to_json(self) -> Text:
    """Returns JSON representation of Position."""
    return json.dumps(self.to_dict())
