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

    self.name = asset_name
    self.tracker = self._id.split(':')[-1]
    self.current_price = asset_price
    self.currency = asset_currency

    self.operations = {}

  def __str__(self):
    """Converts asset to string."""
    return (
        'Asset<'
        f'id: {self._id}, '
        f'tracker: {self.tracker}, '
        f'name: {self.name}, '
        f'price: {self.current_price}, '
        f'currency: {self.currency}'
        '>'
    )

  def get_id(self):
    """Gets asset id (asset code)."""
    return self._id

  def to_dict(self) -> Mapping:
    """Returns Dict represtation of Asset."""
    return {
        'asset_id': self._id,
        'tracker': self.tracker,
        'name': self.name,
        'price': self.current_price,
        'currency': self.currency,
    }

  def to_json(self) -> Text:
    """Returns JSON representation of Asset."""
    return json.dumps(self.to_dict())
