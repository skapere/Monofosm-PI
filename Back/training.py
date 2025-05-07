import pyodbc
import pandas as pd
import numpy as np
import networkx as nx
import itertools
import random
from sklearn.ensemble import RandomForestClassifier
from node2vec import Node2Vec
import joblib
import os


def get_db_connection():
    server = 'localhost'
    database = 'DW_Monoprix'
    driver = '{ODBC Driver 17 for SQL Server}'
    connection_string = f'DRIVER={driver};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    conn = pyodbc.connect(connection_string)
    return conn


def train_and_save_models():
    conn = get_db_connection()
    query = """
    SELECT 
        F.CustomerID,
        F.ProductID
    FROM Fact_SalesPerformance F
    WHERE F.CustomerID IS NOT NULL
    AND F.ProductID IS NOT NULL
    AND F.SalesTransactions_Amount IS NOT NULL
    """
    df = pd.read_sql(query, conn)

    # Build bipartite graph
    B = nx.Graph()
    customers = df['CustomerID'].astype(str).unique()
    products = df['ProductID'].astype(str).unique()

    B.add_nodes_from(customers, bipartite=0)
    B.add_nodes_from(products, bipartite=1)
    edges = list(df.apply(lambda row: (str(row['CustomerID']), str(row['ProductID'])), axis=1))
    B.add_edges_from(edges)

    # Train Node2Vec
    node2vec = Node2Vec(B, dimensions=64, walk_length=10, num_walks=50, workers=1)
    model = node2vec.fit(window=5, min_count=1, batch_words=4)

    product_embeddings = {node: model.wv[node] for node in products}

    # Positive and Negative pairs
    positive_pairs_series = df.groupby('CustomerID')['ProductID'].apply(
        lambda x: list(itertools.combinations(set(x.astype(str)), 2))
    )
    positive_pairs = [pair for sublist in positive_pairs_series for pair in sublist]

    possible_negative_pairs = list(itertools.combinations(products, 2))
    num_neg_samples = min(len(possible_negative_pairs), len(positive_pairs))
    negative_pairs = random.sample(possible_negative_pairs, num_neg_samples)
    positive_pairs = positive_pairs[:num_neg_samples]

    def pair_embedding(pair):
        return np.concatenate([product_embeddings[pair[0]], product_embeddings[pair[1]]])

    X = np.array([pair_embedding(p) for p in positive_pairs + negative_pairs])
    y = np.array([1] * num_neg_samples + [0] * num_neg_samples)

    # Train RandomForest
    rf_clf = RandomForestClassifier()
    rf_clf.fit(X, y)

    # Save models
    os.makedirs('app/app/models', exist_ok=True)
    joblib.dump(rf_clf, 'app/models/rf_model.pkl')
    joblib.dump(product_embeddings, 'app/models/product_embeddings.pkl')

    print("✅ Training complete. Models saved.")


if __name__ == '__main__':
    train_and_save_models()
