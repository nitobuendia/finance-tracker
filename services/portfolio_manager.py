"""Manages operations on a portfolio."""

import glob
import os
import pickle
from models import asset
from models import portfolio
from models import position
from services import file_manager
from typing import Mapping, Sequence, Text

_PORTFOLIO_STORAGE_PATH = 'portfolios'
_PORTFOLIO_GLOB_FILES = f'{_PORTFOLIO_STORAGE_PATH}/*'

_PORTFOLIOS = {}


def create_portfolio(portfolio_name: Text) -> portfolio.Portfolio:
  """Creates a new portoflio.

  Args:
    portfolio_name: Name of the portfolio.

  Returns:
    New Portfolio.
  """
  new_portfolio = portfolio.Portfolio(portfolio_name)
  _store_portfolio(new_portfolio)

  return new_portfolio


def get_porfolio_position(managed_portfolio: portfolio.Portfolio
                          ) -> Mapping[asset.Asset, position.Position]:
  """Gets the position of all assets in the portfolio.

  Args:
    managed_portfolio: Portfolio from which to obtain position.

  Returns:
    Map of assets and their current positions.
  """
  return managed_portfolio.asset_positions


def _get_portfolio_from_file(portfolio_filename: Text) -> portfolio.Portfolio:
  """Gets a porfolio name from a given file name.

  Args:
    portfolio_filename: File where portfolio is stored.

  Returns:
    Portfolio contents.
  """
  portfolio_info = file_manager.get_file_binary_content(portfolio_filename)
  return pickle.loads(portfolio_info)


def get_portfolio(portfolio_id: Text) -> portfolio.Portfolio:
  """Gets a portfolio by given id.

  Args:
    portfolio_id: Portfolio id to retrieve.

  Returns:
    Portfolio. None if it does not exist.
  """
  portfolios = get_portfolios()
  return portfolios.get(portfolio_id)


def get_portfolios() -> Mapping[Text, portfolio.Portfolio]:
  """Gets all available portfolios.

  Returns:
    List of available portfolios.
  """
  global _PORTFOLIOS

  if not _PORTFOLIOS:
    portfolio_filenames = glob.glob(_PORTFOLIO_GLOB_FILES)
    portfolio_list = [
        _get_portfolio_from_file(portfolio_filename)
        for portfolio_filename in portfolio_filenames
    ]

    _PORTFOLIOS = {
        managed_portfolio.get_id(): managed_portfolio
        for managed_portfolio in portfolio_list
    }

  return _PORTFOLIOS


def _store_portfolio(managed_portfolio: portfolio.Portfolio):
  """Stores portoflio contents.

  Args:
    managed_portfolio: Portfolio to store.
  """
  serialized_portfolio = pickle.dumps(managed_portfolio)

  portfolio_filename = (
      f'{_PORTFOLIO_STORAGE_PATH}/{managed_portfolio.get_id()}')
  file_manager.create_file(portfolio_filename, contents=serialized_portfolio)
