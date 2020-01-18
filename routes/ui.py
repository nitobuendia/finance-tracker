"""UI routes for Finance Tracker."""

import flask
from services import asset_manager
from services import operation_manager
from services import portfolio_manager
from services import position_manager
from services import stats_manager

ui_routes = flask.Blueprint('ui', __name__)


@ui_routes.route('/', methods=['GET'])
def get_portfolios():
  portfolios = portfolio_manager.get_portfolios()
  return flask.render_template(
      'views/portfolios.jinja2', portfolios=portfolios)


@ui_routes.route('/portfolios/<portfolio_id>/', methods=['GET'])
def get_portfolio(portfolio_id):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  portfolio_positions = position_manager.get_positions(managed_portfolio)

  return flask.render_template(
      'views/portfolio.jinja2',
      portfolio=managed_portfolio,
      portfolio_positions=portfolio_positions,
  )


@ui_routes.route('/portfolios/<portfolio_id>/history/', methods=['GET'])
def get_portfolio_history(portfolio_id):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  portfolio_operations = operation_manager.get_operations(managed_portfolio)

  return flask.render_template(
      'views/portfolio_history.jinja2',
      portfolio=managed_portfolio,
      portfolio_operations=portfolio_operations,
  )


@ui_routes.route('/portfolios/<portfolio_id>/stats/', methods=['GET'])
def get_portfolio_stats(portfolio_id):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  portfolio_stats = stats_manager.get_portfolio_stats(managed_portfolio)

  return flask.render_template(
      'views/portfolio_stats.jinja2',
      portfolio=managed_portfolio,
      portfolio_stats=portfolio_stats,
  )


@ui_routes.route(
    '/portfolios/<portfolio_id>/assets/<asset_name>/', methods=['GET'])
def get_asset(portfolio_id, asset_name):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  managed_asset = asset_manager.get_asset(managed_portfolio, asset_name)
  asset_operations = asset_manager.get_operations(managed_asset)
  asset_position = position_manager.get_position(managed_asset)

  return flask.render_template(
      'views/asset.jinja2',
      portfolio=managed_portfolio,
      asset=managed_asset,
      asset_operations=asset_operations,
      asset_position=asset_position,
  )
