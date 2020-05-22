import json
import uuid
from typing import Mapping, Optional, Sequence, Text

_DEFAULT_CURRENCY = 'USD'


class Portfolio(object):
  """Represents a collection of assets and operations on them."""

  def __init__(self, portfolio_name: Text,
               portfolio_currency: Optional[Text] = _DEFAULT_CURRENCY):
    """Instantiates a Portfolio.

    Args:
      portfolio_name: Name of the portfolio.
      portfolio_currency: Currency in which portfolio operates.
    """
    self._id = str(uuid.uuid4())
    self.assets = {}

    self.name = portfolio_name
    self.currency = portfolio_currency

  def __str__(self):
    """Converts Portfolio to string."""
    return f'Portfolio<id: {self._id}, portfolio_name: {self.name}>'

  def get_id(self) -> Text:
    """Returns portfolio id."""
    return self._id

  def get_name(self) -> Text:
    """Returns portfolio name."""
    return f'{self.name} ({self._id})'

  def to_dict(self) -> Mapping:
    """Returns Dict represtation of Portfolio."""
    return {
        'portfolio_id': self._id,
        'name': self.name,
        'portfolio_currency': self.currency,
    }

  def to_json(self):
    """Returns JSON representation of Portfolio."""
    return json.dumps(self.to_dict())
