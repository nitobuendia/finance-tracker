"""Finance Tracker allows you to track your financial asset operations."""

import flask
from routes import api
from routes import static
from routes import ui

app = flask.Flask(__name__)
app.register_blueprint(api.api_routes)
app.register_blueprint(static.static_routes)
app.register_blueprint(ui.ui_routes)


if __name__ == "__main__":
  app.run(host='0.0.0.0', port=99, debug=True)
