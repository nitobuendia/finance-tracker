import json
import uuid
from typing import Mapping, Optional, Text


class Asset(object):
  """Represents a financial asset."""

  def __init__(self, asset_name: Text, asset_id: Optional[Text] = None):
    """Instantiates financial Asset.

    Args:
      asset_name: Name of the asset to create.
      asset_id: Id of the asset to create.
          Only to be used to load previous state.
    """
    self._id = asset_id or str(uuid.uuid4())
    self.name = asset_name

  def __str__(self):
    """Converts asset to string."""
    return f'Asset<id: {self._id}, name: {self.name}>'

  def to_dict(self) -> Mapping:
    """Returns Dict represtation of Asset."""
    return {
        'asset_id': self._id,
        'name': self.name,
    }

  def to_json(self) -> Text:
    """Returns JSON representation of Asset."""
    return json.dumps(self.to_dict())
