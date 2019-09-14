"""Static file routes for Finance Tracker."""

import flask

static_routes = flask.Blueprint('static', __name__)


@static_routes.route('/css/<path:css_path>', methods=['GET'])
def serve_css(css_path):
  return flask.send_from_directory('static/css', css_path)
