"""API routes for Finance Tracker."""

import datetime
import flask

from services import asset_manager
from services import operation_manager
from services import portfolio_manager

api_routes = flask.Blueprint('api', __name__)


@api_routes.route('/api/portfolios/', methods=['GET'])
def get_portfolios():
  portfolios = portfolio_manager.get_portfolios()
  return flask.jsonify([
      managed_portfolio.to_dict()
      for managed_portfolio in portfolios.values()
  ])


@api_routes.route('/api/portfolios/', methods=['POST'])
def create_portfolio():
  request_data = flask.request.get_json()
  portfolio_name = request_data['name']
  new_portfolio = portfolio_manager.create_portfolio(portfolio_name)
  return new_portfolio.to_dict()


@api_routes.route('/api/portfolios/<portfolio_id>/', methods=['GET'])
def get_portfolio(portfolio_id):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  return managed_portfolio.to_dict()


@api_routes.route('/api/portfolios/<portfolio_id>/assets/', methods=['GET'])
def get_portfolio_assets(portfolio_id):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  portfolio_assets = managed_portfolio.assets
  return flask.jsonify([
      portfolio_asset.to_dict()
      for portfolio_asset in portfolio_assets.values()
  ])


@api_routes.route('/api/portfolios/<portfolio_id>/balance/', methods=['GET'])
def get_portfolio_balance(portfolio_id):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  portfolio_positions = portfolio_manager.get_porfolio_position(
      managed_portfolio)

  portfolio_position_list = {
      managed_asset.name: asset_position.to_dict()
      for managed_asset, asset_position in portfolio_positions.items()
  }

  return portfolio_position_list


@api_routes.route(
    '/api/portfolios/<portfolio_id>/operations/', methods=['GET'])
def get_portfolio_operations(portfolio_id):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  portfolio_positions = managed_portfolio.operations

  return flask.jsonify([
      portfolio_operation.to_dict()
      for portfolio_operation in portfolio_positions
  ])


@api_routes.route(
    '/api/portfolios/<portfolio_id>/assets/<asset_name>/', methods=['GET'])
def get_portfolio_asset(portfolio_id, asset_name):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  managed_asset = asset_manager.get_asset(managed_portfolio, asset_name)
  return managed_asset.to_dict()


@api_routes.route(
    '/api/portfolios/<portfolio_id>/assets/<asset_name>/balance/',
    methods=['GET'])
def get_portfolio_asset_balance(portfolio_id, asset_name):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  managed_asset = asset_manager.get_asset(managed_portfolio, asset_name)
  asset_position = asset_manager.get_asset_position(
      managed_portfolio, managed_asset)
  return asset_position.to_dict()


@api_routes.route(
    '/api/portfolios/<portfolio_id>/assets/<asset_name>/operations/',
    methods=['GET'])
def get_asset_operations(portfolio_id, asset_name):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  managed_asset = asset_manager.get_asset(managed_portfolio, asset_name)

  asset_position = asset_manager.get_asset_position(
      managed_portfolio, managed_asset)
  asset_operations = asset_position.operations

  return flask.jsonify([
      asset_operation.to_dict() for asset_operation in asset_operations])


@api_routes.route(
    '/api/portfolios/<portfolio_id>/assets/<asset_name>/operations/',
    methods=['POST'])
def create_asset_operation(portfolio_id, asset_name):
  request_data = flask.request.get_json()
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)

  timestamp_int = int(request_data['timestamp'])
  timestamp = datetime.datetime.fromtimestamp(timestamp_int)

  operation_type_name = request_data['operation_type']
  operation_type = operation_manager.get_operation_type(operation_type_name)

  quantity = int(request_data['quantity'])
  price_per_unit = float(request_data['price_per_unit'])
  price_currency = request_data['price_currency']

  new_operation = operation_manager.add_operation(
      managed_portfolio, timestamp, asset_name, operation_type, quantity,
      price_per_unit, price_currency)

  return new_operation.to_dict()
