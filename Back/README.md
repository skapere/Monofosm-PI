# 🧠 MONOFOSM Intelligence API

This Flask-based API provides a set of advanced AI/ML-powered services to optimize retail operations. It integrates database-driven analytics, product embeddings, time-series forecasting, supplier recommendations, anomaly detection, and dispute prediction for purchasing workflows.

---

## 🚀 Features

### 📊 Aisle Category Recommendation
- Builds a co-purchase graph from customer-product-category transactions.
- Uses Node2Vec + t-SNE for spatial representation.
- Recommends category placements within store aisle cells.

### 🔍 Supplier Recommendation
- Calculates supplier reliability using dispute rate, price, and transaction volume.
- Applies k-NN to suggest optimal suppliers per product category.
- Country-based prioritization (e.g., `France` first).

### 🧠 Product Pair Recommendation
- Uses a pre-trained RandomForest model and vector embeddings to suggest product pairings.
- Ideal for bundle promotions and layout adjacency decisions.

### 💹 Stock Market Analysis
- Detects anomalies via Isolation Forest.
- Computes daily returns, volatility, and trend.
- Forecasts next 7-day price change using Prophet.
- Computes Value-at-Risk (VaR) with configurable confidence levels.

### 🧾 Invoice Dispute Prediction
- Predicts likelihood of disputes based on invoice metadata using a trained SVM model.
- Includes categorical and numeric preprocessing steps.

### 🗨️ LLM Integration (Mistral)
- Local integration with a self-hosted Mistral model.
- Accepts custom prompts and streams responses.

---

## 🏗️ Project Structure

```plaintext
├──app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Environment-based configuration
│   ├── routes.py                # Flask routes (not shown above)
│   ├── aisles_recom.py          # Category aisle layout optimizer
│   ├── ml_models.py             # Supplier rec, anomalies, forecasts, disputes
│   ├── models/                  # Serialized models (.pkl)
│   └── templates/               # (Optional) HTML templates for Swagger or views
│   .env                         # Environment variables
│   run.py                       # App entry point
└── requirements.txt             # Python dependencies
