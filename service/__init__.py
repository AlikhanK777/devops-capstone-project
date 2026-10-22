
"""
Package: service
Package for the application models and service routes.

This module creates and configures the Flask app,
sets up logging, security headers, CORS, and the SQL database.
"""

import sys

from flask import Flask
from flask_talisman import Talisman
from flask_cors import CORS

from service import config
from service.common import log_handlers


# Create Flask application
app = Flask(__name__)
app.config.from_object(config)


# Configure security headers using Flask-Talisman.
# HTTPS redirection is disabled for local development and testing.
talisman = Talisman(
    app,
    force_https=False,
    content_security_policy=None,
)


# Enable Cross-Origin Resource Sharing for the Accounts REST API.
# Allow all origins for the educational project.
CORS(
    app,
    resources={
        r"/accounts": {"origins": "*"},
        r"/accounts/*": {"origins": "*"},
    },
)


# Import routes and models after the Flask app is created.
# pylint: disable=wrong-import-position, cyclic-import, wrong-import-order
from service import routes, models  # noqa: F401 E402

# pylint: disable=wrong-import-position
from service.common import error_handlers, cli_commands  # noqa: F401 E402


# Set up logging for production
log_handlers.init_logging(app, "gunicorn.error")

app.logger.info(70 * "*")
app.logger.info(
    "  A C C O U N T   S E R V I C E   R U N N I N G  ".center(70, "*")
)
app.logger.info(70 * "*")


# Initialize database tables
try:
    models.init_db(app)
except Exception as error:  # pylint: disable=broad-except
    app.logger.critical("%s: Cannot continue", error)
    # Gunicorn requires exit code 4 to stop spawning workers when they die.
    sys.exit(4)


app.logger.info("Service initialized!")
