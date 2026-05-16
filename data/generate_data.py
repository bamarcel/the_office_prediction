import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Stores
stores_data = {
    'store_id': [1, 2, 3],
    'store_name': ['Scranton Branch', 'Stamford Branch', 'Nashua Branch'],
    'city': ['Scranton', 'Stamford', 'Nashua'],
    'manager': ['Michael Scott', 'Josh Porter', 'Craig']
}
stores_df = pd.DataFrame(stores_data)

# Sellers
sellers_data = {
    'seller_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    'seller_name': ['Jim Halpert', 'Dwight Schrute', 'Phyllis Vance', 'Stanley Hudson', 'Andy Bernard', 'Angela Martin', 'Karen Filippelli', 'Oscar Martinez', 'Kevin Malone', 'Meredith Palmer'],
    'store_id': [3, 1, 3, 3, 1, 1, 3, 2, 2, 2] 
}
sellers_df = pd.DataFrame(sellers_data)

# Products
products_data = {
    'product_id': [1, 2, 3, 4, 5],
    'product_name': ['Premium Paper', 'Copy Paper', 'Cardstock', 'Envelopes', 'Notepads'],
    'unit_price': [15.99, 7.99, 12.49, 4.99, 5.49]
}
products_df = pd.DataFrame(products_data)

# --- Génération de nouvelles données à grande échelle et asymétriques ---

# 1. Customers (1000 clients)
num_customers = 1000
cities = ['Nashua', 'New York', 'Boston', 'Stamford', 'Scranton']
new_customers_data = {
    'customer_id': range(1, num_customers + 1),
    'customer_name': [f'Customer {i}' for i in range(1, num_customers + 1)],
    'city': np.random.choice(cities, num_customers, p=[0.25, 0.2, 0.2, 0.15, 0.2]) # Distribution inégale des villes
}
customers_df = pd.DataFrame(new_customers_data)

# 2. Orders (10000 commandes)
num_orders = 10000
start_date = datetime(2023, 1, 1)
end_date = datetime(2026, 12, 31)

# Fonction pour générer des dates aléatoires avec saisonnalité
#### Plus de commandes en janvier, septembre et décembre pour être plus proche de la logique métier
def random_dates_with_seasonality(start, end, n):
    all_dates = pd.date_range(start=start, end=end, freq='D')

    # Poids saisonniers par mois (hypothèse métier)
    month_weights = {
        1: 1.4,   # Janvier (nouveaux budgets)
        2: 1.0,
        3: 1.0,
        4: 1.0,
        5: 1.0,
        6: 0.9,
        7: 0.6,   # Été (creux)
        8: 0.6,   # Été (creux)
        9: 1.4,   # Rentrée
        10: 1.1,
        11: 1.0,
        12: 1.4   # Fin d’année
    }

    # Appliquer les poids aux dates
    weights = np.array([month_weights[d.month] for d in all_dates])
    weights = weights / weights.sum()

    sampled_dates = np.random.choice(all_dates, size=n, p=weights)
    return pd.to_datetime(sampled_dates)


# Définition des probabilités d'inclinaison pour les vendeurs (sellers)
# Par exemple, Jim et Dwight sont plus performants que Meredith.
seller_ids = sellers_df['seller_id'].tolist()
seller_probs = [0.15, 0.20, 0.10, 0.05, 0.10, 0.05, 0.15, 0.05, 0.10, 0.05] # La somme doit faire 1.0

new_orders_data = {
    'order_id': range(1, num_orders + 1),
    'customer_id': np.random.randint(1, num_customers + 1, num_orders),
    'seller_id': np.random.choice(seller_ids, num_orders, p=seller_probs),
    'order_date': [d.strftime('%Y-%m-%d') for d in random_dates_with_seasonality(start_date, end_date, num_orders)]
}
orders_df = pd.DataFrame(new_orders_data)
orders_df = orders_df.sort_values(by='order_date').reset_index(drop=True)

# 3. Order Items (10000 lignes)
num_order_items = 15000
product_ids = products_df['product_id'].tolist()
product_unit_prices = products_df.set_index('product_id')['unit_price'].to_dict()

# Définition des probabilités d'inclinaison pour les produits (Copy Paper, Premium Paper sont populaires)
product_probs = [0.25, 0.35, 0.15, 0.10, 0.15] # La somme doit faire 1.0

# Couverture des commandes avec au moins un article 
new_order_items_data = {
    'order_id': range(1, num_orders + 1),
    'product_id': np.random.choice(product_ids, num_orders, p=product_probs),
    'quantity': np.random.randint(1, 10, num_orders),
}

# Ajout d'articles
additonnal_order_items_data = {
    'order_id': np.random.randint(1, num_orders + 1, num_order_items),
    'product_id': np.random.choice(product_ids, num_order_items, p=product_probs),
    'quantity': np.random.randint(1, 10, num_order_items),
}

order_items_df = pd.DataFrame(new_order_items_data)
order_items_df = pd.concat([order_items_df, pd.DataFrame(additonnal_order_items_data)], ignore_index=True)

# --- Sauvegarde des nouveaux fichiers CSV ---

output_files = {
    "customers.csv": customers_df,
    "orders.csv": orders_df,
    "order_items.csv": order_items_df,
    "products.csv": products_df,
    "sellers.csv": sellers_df,
    "stores.csv": stores_df,
}

for filename, df in output_files.items():
    df.to_csv("data/" + filename, index=False)
    print(f"Fichier généré : {filename} avec {len(df)} lignes.")

# Afficher les premières lignes et les tailles pour vérification
print("\n--- Aperçu des nouveaux fichiers ---")
print(f"customers_large.csv ({len(customers_df)} lignes):\n", customers_df.head())
print(f"\norders_large.csv ({len(orders_df)} lignes):\n", orders_df.head())
print(f"\norder_items_large.csv ({len(order_items_df)} lignes):\n", order_items_df.head())