import json
import uuid
from typing import Mapping, Optional, Text


class Asset(object):
  """Represents a financial asset."""

  def __init__(
          self, asset_code: Text, asset_name: Text, asset_price: float,
          asset_currency: Text):
    """Instantiates financial Asset.

    Args:
      managed_portfolio: Portfolio where asset is created.
      asset_code: Asset code or id to create. Must be unique.
      asset_name: Full name of the asset.
      asset_price: Current asset price.
      asset_currency: Currency of the asset.
    """
    self._id = asset_code
    self.tracker = self.get_tracker()

    self.name = asset_name
    self.current_price = asset_price
    self.currency = asset_currency

    self.operations = {}
    self.stats = None

  def __str__(self):
    """Converts asset to string."""
    return (
        'Asset<'
        f'id: {self.get_id()}, '
        f'tracker: {self.get_tracker()}, '
        f'name: {self.name}, '
        f'price: {self.current_price}, '
        f'currency: {self.currency}'
        '>'
    )

  def get_id(self):
    """Gets asset id (asset code)."""
    return self._id

  def get_tracker(self):
    """Gets the asset tracker code, which is used to obtain data."""
    if not hasattr(self, 'tracker') or not self.tracker:
      self.tracker = self._id.split(':')[-1] or self._id
    return self.tracker

  def to_dict(self) -> Mapping:
    """Returns Dict represtation of Asset."""
    return {
        'asset_id': self.get_id(),
        'tracker': self.get_tracker(),
        'name': self.name,
        'price': self.current_price,
        'currency': self.currency,
    }

  def to_json(self) -> Text:
    """Returns JSON representation of Asset."""
    return json.dumps(self.to_dict())
