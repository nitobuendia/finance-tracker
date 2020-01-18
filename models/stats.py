import abc
import json
from models import asset
from typing import Mapping, Text, Union


class AssetStats(abc.ABC):
  """Representations of stats for any type of asset."""

  @abc.abstractmethod
  def __init__(self, managed_asset: asset.Asset):
    pass

  @abc.abstractmethod
  def to_dict(self) -> Mapping:
    pass

  @abc.abstractmethod
  def to_json(self) -> Text:
    pass


class StockStats(object):
  """Represents key financial stats for a Stock."""

  def __init__(self,
               managed_asset: asset.Asset,
               price: float = None,
               debt_to_equity: float = None,
               dividend_yield: float = None,
               eps: float = None,
               pe: float = None,
               profit_margin: float = None,
               return_on_equity: float = None,
               revenue_growth: float = None,
               value_over_ebitda: float = None):
    """Initializes stock financial stats.

    Args:
      managed_asset: Asset for which to represent stats.
      price: Price of the stock.
      debt_to_equity: Debt to equity financial ration.
      dividend_yield: 5 year dividend yield.
      eps: Earnings per share.
      pe: Price over earnings.
      profit_margin: Profit margin.
      return_on_equity: Return on equity.
      revenue_growth: Revenue growth (YoY).
      value_over_ebitda: Equity value over EBITDA.
    """
    self.asset = managed_asset
    self.price = price
    self.debt_to_equity = debt_to_equity
    self.dividend_yield = dividend_yield
    self.eps = eps
    self.pe = pe
    self.profit_margin = profit_margin
    self.return_on_equity = return_on_equity
    self.revenue_growth = revenue_growth
    self.value_over_ebitda = value_over_ebitda

  def to_dict(self) -> Mapping:
    """Returns Dict representation of StockStats."""
    return {
        'asset': self.asset.get_id(),
        'price': self.price,
        'debt_to_equity': self.debt_to_equity,
        'dividend_yield': self.dividend_yield,
        'eps': self.eps,
        'pe': self.pe,
        'profit_margin': self.profit_margin,
        'return_on_equity': self.return_on_equity,
        'revenue_growth': self.revenue_growth,
        'value_over_ebitda': self.value_over_ebitda
    }

  def to_json(self) -> Text:
    """Returns JSON representation of StockStats."""
    return json.dumps(self.to_dict())
