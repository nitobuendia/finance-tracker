import json
import uuid
from typing import Mapping, Optional, Text

_DEFAULT_CURRENCY = 'USD'


class Portfolio(object):
  """Represents a collection of assets and operations on them."""

  def __init__(self, portfolio_name: Text,
               portfolio_currency: Optional[Text] = _DEFAULT_CURRENCY,
               portfolio_id: Optional[Text] = None):
    """Instantiates a Portfolio.

    Args:
      portfolio_name: Name of the portfolio.
      porfolio_currency: Currency in which porfolio operates.
      portfolio_id: Id of the portfolio to create.
          Only to be used to load previous state.
    """
    self._id = portfolio_id or str(uuid.uuid4())
    self.name = portfolio_name
    self.currency = portfolio_currency

    self.operations = []
    self.assets = {}
    self.asset_positions = {}

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
