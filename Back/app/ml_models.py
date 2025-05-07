# app/ml_models.py

import pyodbc
import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
import itertools
import random
import joblib
import os
import json
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
from prophet import Prophet
import requests
from dotenv import load_dotenv

load_dotenv()


# --- Step 1: Database connection ---
def get_db_connection():
    conn = pyodbc.connect(
        f"DRIVER={{{os.getenv('SQL_DRIVER')}}};"
        f"SERVER={os.getenv('SQL_SERVER')};"
        f"DATABASE={os.getenv('SQL_DATABASE')};"
        "Trusted_Connection=yes;"
    )
    return conn


# --- Step 2: Load and preprocess data ---
def load_supplier_data():
    conn = get_db_connection()
    query = """
    SELECT
        S.PK_Supplier,
        S.Name AS SupplierName,
        S.Country,
        S.City,
        C.BK_Category AS Category,
        AVG(F.Product_SupplierPrice) AS AvgSupplierPrice,
        COUNT(F.InvoiceID) AS NumberOfTransactions,
        SUM(CASE WHEN F.DisputeID IS NOT NULL THEN 1 ELSE 0 END) * 1.0 / NULLIF(COUNT(F.InvoiceID), 0) AS DisputeRate
    FROM Fact_SupplierManagement F
    LEFT JOIN DimSupplier S ON F.SupplierID = S.PK_Supplier
    LEFT JOIN DimCategory C ON F.CategoryID = C.PK_Category
    GROUP BY
        S.PK_Supplier, S.Name, S.Country, S.City, C.BK_Category
    ORDER BY
        C.BK_Category, DisputeRate ASC, AvgSupplierPrice ASC;
    """
    df = pd.read_sql(query, conn)

    # Fill missing values
    df[['AvgSupplierPrice', 'DisputeRate']] = df[['AvgSupplierPrice', 'DisputeRate']].fillna(0)
    mean_supplier_price = df[df['AvgSupplierPrice'] != 0]['AvgSupplierPrice'].mean()
    df['AvgSupplierPrice'] = df['AvgSupplierPrice'].replace(0, mean_supplier_price)

    df[['SupplierName', 'Country', 'City']] = df[['SupplierName', 'Country', 'City']].fillna('UNKNOWN')
    df['Country'] = df['Country'].str.strip().replace('', 'UNKNOWN')
    df['City'] = df['City'].str.strip().replace('', 'UNKNOWN')

    return df


# --- Step 3: Recommend suppliers ---
def recommend_suppliers(category, n_recommendations=5, preferred_country='France'):
    df = load_supplier_data()
    df_suppliers = df.dropna()

    features = ['AvgSupplierPrice', 'DisputeRate', 'NumberOfTransactions']
    category_df = df_suppliers[df_suppliers['Category'] == category]

    if category_df.empty:
        return {"message": "No suppliers available for this category."}

    n_neighbors = min(n_recommendations + 1, len(category_df))
    if n_neighbors <= 1:
        return {"message": f"Not enough suppliers in category {category} for recommendations."}

    scaler = MinMaxScaler()
    category_scaled = scaler.fit_transform(category_df[features])

    knn = NearestNeighbors(n_neighbors=n_neighbors, metric='euclidean')
    knn.fit(category_scaled)

    random_supplier_index = np.random.randint(0, len(category_df))
    distances, indices = knn.kneighbors([category_scaled[random_supplier_index]])

    idx_list = indices.flatten()[1:]

    recommendations = []
    for pos in idx_list:
        supplier = category_df.iloc[pos]
        has_disputes = "Has Disputes" if float(supplier['DisputeRate']) > 0 else "No Disputes"
        supplier_id = supplier['PK_Supplier']
        original_price = df[df['PK_Supplier'] == supplier_id]['AvgSupplierPrice'].values[0]

        recommendations.append({
            'SupplierName': str(supplier['SupplierName']),
            'Country': str(supplier['Country']),
            'AvgSupplierPrice': float(original_price),
            'HasDisputes': str(has_disputes),  # STR not BOOL!
            'NumberOfTransactions': int(supplier['NumberOfTransactions'])
        })

    # Sort France suppliers first
    recommendations_sorted = sorted(
        recommendations,
        key=lambda x: (x['Country'] != preferred_country, x['AvgSupplierPrice'])
    )

    return recommendations_sorted


#! ------------------------------


# Load pre-trained model and embeddings
model_path = os.path.join('app', 'models', 'rf_model.pkl')
embeddings_path = os.path.join('app', 'models', 'product_embeddings.pkl')

rf_clf = joblib.load(model_path)
product_embeddings = joblib.load(embeddings_path)


def get_product_name_mapping():
    conn = get_db_connection()
    query = """
    SELECT PK_Product, Name
    FROM [DW_Monoprix].[dbo].[DimProduct]
    """
    df = pd.read_sql(query, conn)
    return dict(zip(df['PK_Product'].astype(str), df['Name']))


def get_top_product_pairs(n_pairs=20):
    products = list(product_embeddings.keys())
    product_name_mapping = get_product_name_mapping()

    # Random product pairs
    possible_pairs = list(itertools.combinations(products, 2))
    sampled_pairs = random.sample(possible_pairs, min(500, len(possible_pairs)))

    def pair_embedding(pair):
        return np.concatenate([product_embeddings[pair[0]], product_embeddings[pair[1]]])

    X_pairs = np.array([pair_embedding(pair) for pair in sampled_pairs])
    y_probas = rf_clf.predict_proba(X_pairs)[:, 1]

    pair_scores = list(zip(sampled_pairs, y_probas))
    sorted_pairs = sorted(pair_scores, key=lambda x: x[1], reverse=True)

    top_pairs = []
    for (prod1, prod2), score in sorted_pairs[:n_pairs]:
        top_pairs.append({
            "product1_name": product_name_mapping.get(str(prod1), "Unknown"),
            "product2_name": product_name_mapping.get(str(prod2), "Unknown"),
            "score": float(score)
        })

    return top_pairs


#! ------------------------------


# --- Load Stock Data ---
def load_stock_data():
    conn = get_db_connection()
    query = """
    SELECT 
        DSE.BK_StockExchange,
        DD.FullDate AS SEDate,
        F.Bource_LastPrice AS LastPrice,
        F.Bource_OpeningPrice AS OpeningPrice,
        F.Bource_HighestPrice AS HighestPrice,
        F.Bource_LowestPrice AS LowestPrice,
        F.Bource_ChangeSinceJan1st AS ChangeSinceJan1st,
        F.Bource_TradingVolume AS TradingVolume
    FROM Fact_FinancialAndAccountingManagement F
    LEFT JOIN DimStockExchange DSE ON F.StockExchangeID = DSE.PK_StockExchange
    LEFT JOIN DimDate DD ON F.SEDateID = DD.PK_Date
    WHERE DSE.BK_StockExchange IS NOT NULL
    ORDER BY DSE.BK_StockExchange, DD.FullDate
    """
    df = pd.read_sql(query, conn)
    df['SEDate'] = pd.to_datetime(df['SEDate'])

    features = ['LastPrice', 'OpeningPrice', 'HighestPrice', 'LowestPrice', 'ChangeSinceJan1st', 'TradingVolume']
    scaler = MinMaxScaler()
    df[features] = scaler.fit_transform(df[features])

    df['Anomaly'] = 0
    for stock in df['BK_StockExchange'].unique():
        temp = df[df['BK_StockExchange'] == stock]
        if len(temp) >= 10:
            model = IsolationForest(n_estimators=100, contamination=0.02, random_state=42)
            preds = model.fit_predict(temp[features])
            df.loc[temp.index, 'Anomaly'] = preds

    df['AnomalyLabel'] = df['Anomaly'].apply(lambda x: 'Anomaly' if x == -1 else 'Normal')
    return df


def explain_anomaly(row):
    reasons = []
    if row['TradingVolume'] > 0.8:
        reasons.append("high trading volume")
    if row['ChangeSinceJan1st'] < 0.2:
        reasons.append("drop since January")
    if row['LastPrice'] < 0.3:
        reasons.append("unusual low price")
    return " and ".join(reasons) if reasons else "general unusual behavior"


def get_anomalies_for_stock(stock):
    df = load_stock_data()
    subset = df[(df['BK_StockExchange'] == stock) & (df['AnomalyLabel'] == 'Anomaly')]
    result = []
    for _, row in subset.iterrows():
        result.append({
            'SEDate': row['SEDate'],
            'LastPrice': float(row['LastPrice']),
            'TradingVolume': float(row['TradingVolume']),
            'Reason': explain_anomaly(row)
        })
    return result


def get_performance_for_stock(stock):
    df = load_stock_data()
    temp = df[df['BK_StockExchange'] == stock].copy()
    temp = temp.sort_values('SEDate')
    temp['DailyReturn'] = temp['LastPrice'].pct_change()

    avg_return = temp['DailyReturn'].mean() * 100
    volatility = temp['DailyReturn'].std() * 100
    if len(temp) >= 7:
        trend = 'Upward 📈' if temp['LastPrice'].iloc[-1] > temp['LastPrice'].iloc[-7] else 'Downward 📉'
    else:
        trend = 'Not enough data'

    return {
        'AverageReturn': avg_return,
        'Volatility': volatility,
        'Trend': trend
    }


def forecast_stock(stock, days_ahead=7):
    df = load_stock_data()
    temp = df[df['BK_StockExchange'] == stock].copy()
    temp = temp[['SEDate', 'LastPrice']].sort_values('SEDate')
    if len(temp) < 10:
        return None

    temp.rename(columns={'SEDate': 'ds', 'LastPrice': 'y'}, inplace=True)
    model = Prophet(daily_seasonality=True)
    model.fit(temp)
    future = model.make_future_dataframe(periods=days_ahead)
    forecast = model.predict(future)

    last_real = temp['y'].iloc[-1]
    future_val = forecast['yhat'].iloc[-1]
    change = ((future_val - last_real) / last_real) * 100
    confidence = min(max(100 - abs(change) * 5, 50), 95)
    return {
        'PredictedChange': change,
        'Confidence': confidence
    }


def compute_var(stock, confidence_level=0.95):
    df = load_stock_data()
    temp = df[df['BK_StockExchange'] == stock].copy().sort_values('SEDate')
    temp['DailyReturn'] = temp['LastPrice'].pct_change().dropna()
    if len(temp['DailyReturn']) < 30:
        return None
    var = np.percentile(temp['DailyReturn'], (1 - confidence_level) * 100)
    return var * 100


# --- Ask Local Mistral LLM ---
def ask_llm(prompt, model="mistral"):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt},
            stream=True
        )

        full_response = ''
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                full_response += data.get('response', '')

        return full_response

    except Exception as e:
        return f"LLM Error: {str(e)}"


#! ------------------------------

# --- Predict Dispute Using SVM ---
sco_model_path = os.path.join('app', 'models', 'sco_purchasing_director_model.pkl')
sco_scaler_path = os.path.join('app', 'models', 'sco_purchasing_director_scaler.pkl')

sco_model = joblib.load(sco_model_path)
sco_scaler = joblib.load(sco_scaler_path)


def predict_dispute(invoice_data: dict):
    df = pd.DataFrame([invoice_data])

    numeric = ['Invoice_Amount', 'Invoice_VATRate', 'Product_Price', 'Delay_Invoice', 'Delay_Payment']
    df[numeric] = df[numeric].fillna(0)
    df[['Origin', 'Category']] = df[['Origin', 'Category']].fillna('UNSPECIFIED')
    df[['Country', 'City']] = df[['Country', 'City']].fillna('UNKNOWN')

    df_encoded = pd.get_dummies(df, columns=['Country', 'City', 'Origin', 'Category'], drop_first=True)

    model_cols = sco_model.feature_names_in_
    for col in set(model_cols) - set(df_encoded.columns):
        df_encoded[col] = 0
    df_encoded = df_encoded[model_cols]

    X_scaled = sco_scaler.transform(df_encoded)
    prediction = int(sco_model.predict(X_scaled)[0])
    return {'Predicted_Dispute': prediction}
