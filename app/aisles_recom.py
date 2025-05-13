import pyodbc
import pandas as pd
import numpy as np
import itertools
from collections import defaultdict
import networkx as nx
from node2vec import Node2Vec
from sklearn.manifold import TSNE
import json
import os


def get_db_connection():
    conn = pyodbc.connect(
        f"DRIVER={{{os.getenv('SQL_DRIVER')}}};"
        f"SERVER={os.getenv('SQL_SERVER')};"
        f"DATABASE={os.getenv('SQL_DATABASE')};"
        "Trusted_Connection=yes;"
    )
    return conn


def recommend_category_placement(store_data):
    grid = store_data["grid"]

    # Connect to SQL Server
    conn = get_db_connection()
    query = """
    SELECT 
        F.CustomerID,
        F.ProductID,
        D.BK_Category
    FROM Fact_SalesPerformance F
    JOIN DimProduct P ON F.ProductID = P.PK_Product
    JOIN DimCategory D ON F.CategoryID = D.PK_Category
    WHERE F.CustomerID IS NOT NULL
      AND F.ProductID IS NOT NULL
      AND F.SalesTransactions_Amount IS NOT NULL
    """
    df = pd.read_sql(query, conn)

    # Build co-purchase graph
    category_pairs = defaultdict(int)
    grouped = df.groupby("CustomerID")["BK_Category"].apply(set)
    for cats in grouped:
        for c1, c2 in itertools.combinations(sorted(cats), 2):
            category_pairs[(c1, c2)] += 1

    G = nx.Graph()
    for (c1, c2), weight in category_pairs.items():
        G.add_edge(c1, c2, weight=weight)

    # Embedding
    category2vec = Node2Vec(G, dimensions=16, walk_length=10, num_walks=50, workers=2)
    category_model = category2vec.fit(window=3, min_count=1)
    category_embeddings = {node: category_model.wv[node] for node in G.nodes}

    # Dimensionality reduction
    X = np.array(list(category_embeddings.values()))
    category_names = list(category_embeddings.keys())
    tsne = TSNE(n_components=2, perplexity=5, random_state=42)
    X_2d = tsne.fit_transform(X)
    category_coords = dict(zip(category_names, X_2d))

    # Find Aisle cells
    aisle_cells = [
        (i, j)
        for i, row in enumerate(grid)
        for j, cell in enumerate(row)
        if cell.get("type") == "Aisle"
    ]

    aisle_cells = sorted(aisle_cells, key=lambda idx: (grid[idx[0]][idx[1]]["y"], grid[idx[0]][idx[1]]["x"]))

    # Assign categories to aisle cells
    ordered_categories = sorted(category_coords.items(), key=lambda x: (x[1][1], x[1][0]))
    assigned_categories = [cat for cat, _ in ordered_categories[:len(aisle_cells)]]

    # Modify grid in-place
    for (i, j), category in zip(aisle_cells, assigned_categories):
        grid[i][j]["type"] = f"Aisle - {category}"

    return grid



