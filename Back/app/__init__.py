#app/__init__.py

from flask import Flask
from flasgger import Swagger
from .config import Config
from .routes import api_blueprint
from flask_pymongo import PyMongo
from flask_cors import CORS

mongo = PyMongo()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Mongo
    mongo.init_app(app)

    # Enable CORS for all routes
    CORS(app)

    # Initialize Swagger
    Swagger(app)

    # Register API routes
    app.register_blueprint(api_blueprint)

    return app
