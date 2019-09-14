"""API routes for Finance Tracker."""

import datetime
import flask

from services import asset_manager
from services import operation_manager
from services import portfolio_manager
from services import position_manager

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
  new_portfolio = portfolio_manager.add_portfolio(portfolio_name)
  return new_portfolio.to_dict()


@api_routes.route('/api/portfolios/<portfolio_id>/', methods=['GET'])
def get_portfolio(portfolio_id):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  return managed_portfolio.to_dict()


@api_routes.route('/api/portfolios/<portfolio_id>/assets/', methods=['GET'])
def get_portfolio_assets(portfolio_id):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  portfolio_assets = asset_manager.get_assets(managed_portfolio)
  return flask.jsonify([
      portfolio_asset.to_dict()
      for portfolio_asset in portfolio_assets.values()
  ])


@api_routes.route('/api/portfolios/<portfolio_id>/assets/', methods=['POST'])
def create_portfolio_asset(portfolio_id):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)

  request_data = flask.request.get_json()

  asset_code = request_data['asset_code']
  asset_name = request_data.get('asset_name', asset_code)
  asset_price = float(request_data.get('asset_price', 0))
  asset_currency = request_data.get(
      'asset_currency', managed_portfolio.currency)

  managed_asset = asset_manager.add_asset(
      managed_portfolio, asset_code, asset_name, asset_price, asset_currency)

  return managed_asset.to_dict()


@api_routes.route('/api/portfolios/<portfolio_id>/position/', methods=['GET'])
def get_portfolio_balance(portfolio_id):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  portfolio_positions = position_manager.get_positions(managed_portfolio)

  portfolio_position_list = {
      managed_asset.get_id(): asset_position.to_dict()
      for managed_asset, asset_position in portfolio_positions.items()
  }

  return portfolio_position_list


@api_routes.route(
    '/api/portfolios/<portfolio_id>/operations/', methods=['GET'])
def get_portfolio_operations(portfolio_id):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  portfolio_positions = operation_manager.get_operations(managed_portfolio)

  return flask.jsonify([
      portfolio_operation.to_dict()
      for portfolio_operation in portfolio_positions
  ])


@api_routes.route(
    '/api/portfolios/<portfolio_id>/assets/<asset_code>/',
    methods=['GET'])
def get_portfolio_asset(portfolio_id, asset_code):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  managed_asset = asset_manager.get_asset(managed_portfolio, asset_code)
  return managed_asset.to_dict()


@api_routes.route(
    '/api/portfolios/<portfolio_id>/assets/<asset_name>/position/',
    methods=['GET'])
def get_portfolio_asset_balance(portfolio_id, asset_name):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  managed_asset = asset_manager.get_asset(managed_portfolio, asset_name)
  asset_position = position_manager.get_position(managed_asset)
  return asset_position.to_dict()


@api_routes.route(
    '/api/portfolios/<portfolio_id>/assets/<asset_name>/operations/',
    methods=['GET'])
def get_asset_operations(portfolio_id, asset_name):
  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  managed_asset = asset_manager.get_asset(managed_portfolio, asset_name)
  asset_operations = asset_manager.get_operations(managed_asset)

  return flask.jsonify([
      asset_operation.to_dict() for asset_operation in asset_operations])


@api_routes.route(
    '/api/portfolios/<portfolio_id>/assets/<asset_code>/operations/',
    methods=['POST'])
def create_asset_operation(portfolio_id, asset_code):
  request_data = flask.request.get_json()

  managed_portfolio = portfolio_manager.get_portfolio(portfolio_id)
  managed_asset = asset_manager.get_asset(managed_portfolio, asset_code)

  timestamp_int = int(request_data['timestamp'])
  timestamp = datetime.datetime.fromtimestamp(timestamp_int)

  operation_type_name = request_data['operation_type']
  operation_type = operation_manager.get_operation_type(operation_type_name)

  quantity = int(request_data['quantity'])
  price_per_unit = float(request_data['price_per_unit'])
  operation_currency = request_data['operation_currency']

  new_operation = operation_manager.add_operation(
      managed_portfolio, managed_asset, timestamp, operation_type, quantity,
      price_per_unit, operation_currency)

  return new_operation.to_dict()
