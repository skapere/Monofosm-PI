from flask import Blueprint, request, jsonify
from flasgger import swag_from
import pandas as pd
import pyodbc
from app.ml_models import (
    recommend_suppliers,
    get_top_product_pairs, ask_llm, compute_var, forecast_stock, get_performance_for_stock, get_anomalies_for_stock,
    predict_dispute
)
from app.layout_optimizer import generate_layout_template, optimize_layout
import jwt
import datetime
from flask import current_app as app
import os
from dotenv import load_dotenv
from flask_cors import cross_origin
from app.aisles_recom import recommend_category_placement

load_dotenv()

api_blueprint = Blueprint('api', __name__)


#!  -------------------------------------------


@api_blueprint.route('/api/login', methods=['POST'])
def login():
    from app import mongo
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password required'}), 400

    try:
        user = mongo.db.UsersBI.find_one({'email': email})

        if user and user.get('password') == password:
            payload = {
                'username': user.get('username'),
                'email': user.get('email'),
                'role': user.get('role'),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=app.config['JWT_EXPIRATION_SECONDS'])
            }
            token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

            return jsonify({'success': True, 'access_token': token})
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# Database connection
def get_db_connection():
    conn = pyodbc.connect(
        f"DRIVER={{{os.getenv('SQL_DRIVER')}}};"
        f"SERVER={os.getenv('SQL_SERVER')};"
        f"DATABASE={os.getenv('SQL_DATABASE')};"
        f"UID={os.getenv('SQL_USERNAME')};"
        f"PWD={os.getenv('SQL_PASSWORD')}"
    )
    return conn


#! -------------------------------------------
#? Supplier Recommendation API

@api_blueprint.route('/api/recommend_suppliers', methods=['GET'])
@swag_from({
    'tags': ['Supplier Recommendation'],
    'parameters': [
        {
            'name': 'category',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'Product category to recommend suppliers for'
        },
        {
            'name': 'n',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Number of recommendations (default 5)'
        },
        {
            'name': 'preferred_country',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Preferred country for suppliers (default France)'
        }
    ],
    'responses': {
        200: {
            'description': 'Recommended suppliers list'
        }
    }
})
def recommend_suppliers_api():
    category = request.args.get('category')
    n = int(request.args.get('n', 5))
    preferred_country = request.args.get('preferred_country', 'France')

    recommendations = recommend_suppliers(category, n, preferred_country)

    return jsonify({'recommendations': recommendations})


#!  -------------------------------------------
#? Product Recommendation API


@api_blueprint.route('/api/recommend_product_pairs', methods=['GET'])
@swag_from({
    'tags': ['Product Recommendation'],
    'parameters': [
        {
            'name': 'n',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 20,
            'description': 'Number of top product pairs to return'
        }
    ],
    'responses': {
        200: {
            'description': 'List of top product pairs with predicted co-purchase scores',
            'examples': {
                'application/json': {
                    'top_product_pairs': [
                        {"product1": "123", "product2": "456", "score": 0.9123},
                        {"product1": "789", "product2": "101", "score": 0.8547}
                    ]
                }
            }
        }
    }
})
def recommend_product_pairs_api():
    n_pairs = int(request.args.get('n', 20))
    top_pairs = get_top_product_pairs(n_pairs)
    return jsonify({'top_product_pairs': top_pairs})


#!  -------------------------------------------
#? Stock Market APIs

@api_blueprint.route('/api/stock/anomalies', methods=['GET'])
@swag_from({
    'tags': ['Stock Market'],
    'parameters': [
        {'name': 'stock', 'in': 'query', 'type': 'string', 'required': True}
    ],
    'responses': {200: {'description': 'List of anomalies'}}
})
def stock_anomalies_api():
    stock = request.args.get('stock')
    return jsonify({'anomalies': get_anomalies_for_stock(stock)})


@api_blueprint.route('/api/stock/performance', methods=['GET'])
@swag_from({
    'tags': ['Stock Market'],
    'parameters': [
        {'name': 'stock', 'in': 'query', 'type': 'string', 'required': True}
    ],
    'responses': {200: {'description': 'Stock performance metrics'}}
})
def stock_performance_api():
    stock = request.args.get('stock')
    return jsonify({'performance': get_performance_for_stock(stock)})


@api_blueprint.route('/api/stock/forecast', methods=['GET'])
@swag_from({
    'tags': ['Stock Market'],
    'parameters': [
        {'name': 'stock', 'in': 'query', 'type': 'string', 'required': True}
    ],
    'responses': {200: {'description': '7-day stock forecast'}}
})
def stock_forecast_api():
    stock = request.args.get('stock')
    result = forecast_stock(stock)
    if result is None:
        return jsonify({'error': 'Not enough data'}), 400
    return jsonify({'forecast': result})


@api_blueprint.route('/api/stock/risk', methods=['GET'])
@swag_from({
    'tags': ['Stock Market'],
    'parameters': [
        {'name': 'stock', 'in': 'query', 'type': 'string', 'required': True}
    ],
    'responses': {200: {'description': 'Value at Risk'}}
})
def stock_risk_api():
    stock = request.args.get('stock')
    var = compute_var(stock)
    if var is None:
        return jsonify({'error': 'Not enough data'}), 400
    return jsonify({'VaR_1day_95pct': var})


@api_blueprint.route('/api/stock/chatbot', methods=['POST'])
@swag_from({
    'tags': ['Stock Market'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'prompt': {'type': 'string'}
                },
                'required': ['prompt']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Chatbot reply from Mistral',
            'examples': {
                'application/json': {
                    'response': 'Based on recent volume spikes, this may indicate market manipulation.'
                }
            }
        }
    }
})
def stock_chatbot_api():
    data = request.get_json()
    prompt = data.get('prompt')
    if not prompt:
        return jsonify({'error': 'Missing prompt'}), 400
    answer = ask_llm(prompt)
    return jsonify({'response': answer})


#! -------------------------------------------

@api_blueprint.route('/api/invoice/predict-dispute', methods=['POST'])
@swag_from({
    'tags': ['Invoice Classification'],
    'parameters': [{
        'name': 'body',
        'in': 'body',
        'required': True,
        'schema': {
            'type': 'object',
            'properties': {
                'Invoice_Amount': {'type': 'number'},
                'Invoice_VATRate': {'type': 'number'},
                'Product_Price': {'type': 'number'},
                'Delay_Invoice': {'type': 'number'},
                'Delay_Payment': {'type': 'number'},
                'Country': {'type': 'string'},
                'City': {'type': 'string'},
                'Origin': {'type': 'string'},
                'Category': {'type': 'string'}
            },
            'required': ['Invoice_Amount', 'Invoice_VATRate', 'Product_Price', 'Delay_Invoice', 'Delay_Payment']
        }
    }],
    'responses': {
        200: {
            'description': 'Prediction: whether the invoice will result in dispute (0 = No, 1 = Yes)'
        }
    }
})
def predict_dispute_api():
    invoice_data = request.get_json()
    if not invoice_data:
        return jsonify({'error': 'Missing invoice data'}), 400
    price = invoice_data.get('Invoice_Amount')
    print(price)
    result = predict_dispute(invoice_data)
    return jsonify(result)


#! -------------------------------------------
#? Get All Categories

@api_blueprint.route('/api/categories', methods=['GET'])
@swag_from({
    'tags': ['Reference Data'],
    'responses': {
        200: {
            'description': 'Unique list of product categories (BK_Category)',
            'examples': {
                'application/json': {
                    'categories': [
                        "Beverages",
                        "Snacks",
                        "Frozen Foods"
                    ]
                }
            }
        }
    }
})
def get_categories():
    conn = get_db_connection()
    query = "SELECT DISTINCT BK_Category FROM DimCategory WHERE BK_Category IS NOT NULL"
    df = pd.read_sql(query, conn)
    conn.close()

    categories = df['BK_Category'].dropna().unique().tolist()
    return jsonify({'categories': categories})


#! -------------------------------------------
#? Get All Stock Exchanges

@api_blueprint.route('/api/stock_exchanges', methods=['GET'])
@swag_from({
    'tags': ['Reference Data'],
    'responses': {
        200: {
            'description': 'Unique list of stock exchanges (BK_StockExchange)',
            'examples': {
                'application/json': {
                    'stock_exchanges': [
                        "Euronext Paris",
                        "NYSE",
                        "CAC40"
                    ]
                }
            }
        }
    }
})
def get_stock_exchanges():
    conn = get_db_connection()
    query = "SELECT DISTINCT BK_StockExchange FROM DimStockExchange WHERE BK_StockExchange IS NOT NULL"
    df = pd.read_sql(query, conn)
    conn.close()

    exchanges = df['BK_StockExchange'].dropna().unique().tolist()
    return jsonify({'stock_exchanges': exchanges})


#! -------------------------------------------
#? Store Layout Generation API
# app/routes.py

@api_blueprint.route('/api/generate_layout_template', methods=['GET'])
@cross_origin()  # Allow CORS
@swag_from({
    'tags': ['Layout Generation'],
    'parameters': [
        {
            'name': 'width',
            'in': 'query',
            'type': 'number',
            'required': True,
            'description': 'Store width in meters'
        },
        {
            'name': 'height',
            'in': 'query',
            'type': 'number',
            'required': True,
            'description': 'Store height in meters'
        },
        {
            'name': 'cell_size',
            'in': 'query',
            'type': 'number',
            'required': True,
            'description': 'Size of one grid cell in meters'
        }
    ],
    'responses': {
        200: {
            'description': 'Generated layout grid',
            'examples': {
                'application/json': {
                    'grid': [
                        [{'type': 'empty', 'x': 0, 'y': 0}, {'type': 'empty', 'x': 1, 'y': 0}],
                        [{'type': 'shelf', 'x': 0, 'y': 1}, {'type': 'shelf', 'x': 1, 'y': 1}]
                    ],
                    'rows': 2,
                    'cols': 2,
                    'cell_size': 1
                }
            }
        }
    }
})
def generate_layout_template_api():
    width = float(request.args.get('width'))
    height = float(request.args.get('height'))
    cell_size = float(request.args.get('cell_size'))

    layout = generate_layout_template(width, height, cell_size)
    return jsonify(layout)


@api_blueprint.route('/api/optimize_layout', methods=['POST'])
@cross_origin()
@swag_from({
    'tags': ['Layout Optimization'],
    'consumes': ['application/json'],
    'produces': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'grid': {
                        'type': 'array',
                        'items': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'type': {'type': 'string'},
                                    'x': {'type': 'integer'},
                                    'y': {'type': 'integer'}
                                },
                                'required': ['type', 'x', 'y']
                            }
                        }
                    }
                },
                'required': ['grid']
            },
            'description': 'The layout grid to be optimized'
        }
    ],
    'responses': {
        200: {
            'description': 'Optimized layout grid',
            'examples': {
                'application/json': {
                    'grid': [
                        [{'type': 'Door', 'x': 0, 'y': 0}, {'type': 'Cashier', 'x': 1, 'y': 0}],
                        [{'type': 'Walkway', 'x': 0, 'y': 1}, {'type': 'Aisle', 'x': 1, 'y': 1}]
                    ]
                }
            }
        },
        400: {
            'description': 'Invalid input or missing grid'
        }
    }
})
def optimize_layout_api():
    data = request.get_json()
    grid = data.get('grid')
    rows = data.get('rows')
    cols = data.get('cols')
    cell_size = data.get('cell_size')

    if not grid:
        return jsonify({'error': 'Missing layout grid'}), 400

    optimized = optimize_layout(grid, rows, cols, cell_size)
    return jsonify(optimized)


@api_blueprint.route('/api/recommend_category_placement', methods=['POST'])
@cross_origin()
@swag_from({
    'tags': ['Category Placement'],
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'grid': {
                        'type': 'array',
                        'items': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'type': {'type': 'string'},
                                    'x': {'type': 'integer'},
                                    'y': {'type': 'integer'}
                                },
                                'required': ['type', 'x', 'y']
                            }
                        }
                    },
                    'rows': {'type': 'integer'},
                    'cols': {'type': 'integer'},
                    'cell_size': {'type': 'number'}
                },
                'required': ['grid', 'rows', 'cols', 'cell_size']
            },
        }
    ],
    'responses': {
        200: {
            'description': 'Same grid with category names appended to Aisle types'
        }
    }
})
def recommend_category_placement_api():
    data = request.get_json()

    if not data or "grid" not in data:
        return jsonify({'error': 'Missing grid data'}), 400

    try:
        updated_grid = recommend_category_placement(data)
        return jsonify({'grid': updated_grid})
    except Exception as e:
        return jsonify({'error': str(e)}), 500




