from flask import Blueprint, request, jsonify
from flasgger import swag_from
import pandas as pd
import pyodbc
from app.ml_models import (
    recommend_suppliers,
    get_top_product_pairs, ask_llm, compute_var, forecast_stock, get_performance_for_stock, get_anomalies_for_stock,
    predict_dispute
)
from app.layout_optimizer import generate_store_layout, arrange_products
import jwt
import datetime
from flask import current_app as app
import os
from dotenv import load_dotenv

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
#? Store Layout APIs


@api_blueprint.route('/api/generate_store_layout', methods=['POST'])
@swag_from({
    'tags': ['Store Layout'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'shape': {
                        'type': 'string',
                        'enum': ['rectangle', 'L-shape', 'custom'],
                        'default': 'rectangle'
                    },
                    'width': {'type': 'integer', 'default': 5},
                    'height': {'type': 'integer', 'default': 5},
                    'include_butcher': {'type': 'boolean', 'default': True},
                    'include_fruits_vegetables': {'type': 'boolean', 'default': True},
                    'include_spices': {'type': 'boolean', 'default': True},
                    'include_staff_room': {'type': 'boolean', 'default': True}
                },
                'required': ['shape', 'width', 'height']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Generated store layout and special section positions',
            'examples': {
                'application/json': {
                    'layout': [
                        ["Door", "Aisle", "Aisle"],
                        ["Walkway", "Aisle", "Spices"],
                        ["Aisle", "Cashier", "FruitsVeg"]
                    ],
                    'door_position': [0, 0],
                    'cashier_positions': [[2, 0], [2, 1]],
                    'staff_room_position': [2, 2],
                    'butcher_position': [1, 2],
                    'fruits_vegetables_position': [2, 2],
                    'spices_position': [1, 2]
                }
            }
        }
    }
})
def generate_store_layout_api():
    data = request.get_json()
    shape = data.get('shape', 'rectangle')
    width = int(data.get('width', 5))
    height = int(data.get('height', 5))
    include_butcher = data.get('include_butcher', True)
    include_fruits_vegetables = data.get('include_fruits_vegetables', True)
    include_spices = data.get('include_spices', True)
    include_staff_room = data.get('include_staff_room', True)

    result = generate_store_layout(
        shape,
        width,
        height,
        include_butcher=include_butcher,
        include_fruits_vegetables=include_fruits_vegetables,
        include_spices=include_spices,
        include_staff_room=include_staff_room
    )

    response = {
        'layout': result['layout'],
        'door_position': result.get('door_position'),
        'cashier_positions': result.get('cashier_positions'),
        'staff_room_position': result.get('staff_room_position'),
        'butcher_position': result.get('butcher_position'),
        'fruits_vegetables_position': result.get('fruits_vegetables_position'),
        'spices_position': result.get('spices_position')
    }

    return jsonify(response)


@api_blueprint.route('/api/arrange_products', methods=['POST'])
@swag_from({
    'tags': ['Product Arrangement'],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'layout': {
                        'type': 'array',
                        'items': {
                            'type': 'array',
                            'items': {'type': 'string'}
                        },
                        'example': [
                            ["Aisle", "Aisle", "Aisle"],
                            ["Walkway", "Walkway", "Walkway"],
                            ["Aisle", "Aisle", "Aisle"]
                        ]
                    }
                },
                'required': ['layout']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Product pairs assigned to aisle positions',
            'examples': {
                'application/json': {
                    'product_arrangement': [
                        {
                            "product1": "Milk",
                            "product2": "Cereal",
                            "score": 0.89,
                            "product1_position": [0, 0],
                            "product2_position": [0, 1]
                        }
                    ]
                }
            }
        },
        400: {'description': 'Missing layout data'}
    }
})
def arrange_products_api():
    data = request.get_json()
    layout = data.get('layout')

    if not layout:
        return jsonify({'error': 'Missing layout data'}), 400

    product_arrangement = arrange_products(layout)
    return jsonify({'product_arrangement': product_arrangement})
