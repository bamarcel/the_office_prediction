import pandas as pd
import pathlib
import datetime

import connect_db as db

ABSOLUT_PATH = pathlib.Path(__file__).parent.parent 

CUSTOMERS_CSV = ABSOLUT_PATH / "data/customers.csv"
PRODUCTS_CSV = ABSOLUT_PATH / "data/products.csv"
STORES_CSV = ABSOLUT_PATH / "data/stores.csv"
SELLERS_CSV = ABSOLUT_PATH / "data/sellers.csv"
ORDERS_CSV = ABSOLUT_PATH / "data/orders.csv"
ORDER_ITEMS_CSV = ABSOLUT_PATH / "data/order_items.csv"

# Supprime les tables existantes
def deleting_tables(conn):
    print("[" + str(datetime.datetime.now()) + "] — Deleting existing tables...")
    
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS order_items")
    cur.execute("DROP TABLE IF EXISTS orders")
    cur.execute("DROP TABLE IF EXISTS sellers")
    cur.execute("DROP TABLE IF EXISTS stores")
    cur.execute("DROP TABLE IF EXISTS products")
    cur.execute("DROP TABLE IF EXISTS customers")

    conn.commit()

    print("[" + str(datetime.datetime.now()) + "] — Existing tables deleted.")

# Crée les tables nécessaires
def create_table(conn):
    print("[" + str(datetime.datetime.now()) + "] — Creating tables in the database...")

    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            city TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            unit_price REAL
        )
    """)

    cur.execute("""
        CREATE TABLE stores (
            store_id INTEGER PRIMARY KEY AUTOINCREMENT,
            store_name TEXT,
            city TEXT,
            manager TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE sellers (
            seller_id INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_name TEXT,
            store_id INTEGER,
            FOREIGN KEY (store_id) REFERENCES stores(store_id)
        )
    """)

    cur.execute("""
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER,
            seller_id INTEGER,
            order_date TEXT,
            total_amount REAL DEFAULT 0,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
        )
    """)

    cur.execute("""
        CREATE TABLE order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)

    conn.commit()

    print("[" + str(datetime.datetime.now()) + "] — Tables created successfully.") 

# Insère les données depuis les fichiers CSV
def insert_data(conn):
    print("[" + str(datetime.datetime.now()) + "] — Inserting data into the tables...")

    # Lire tous les CSV
    customers_data = pd.read_csv(CUSTOMERS_CSV)
    products_data = pd.read_csv(PRODUCTS_CSV)
    stores_data = pd.read_csv(STORES_CSV)
    sellers_data = pd.read_csv(SELLERS_CSV)
    orders_data = pd.read_csv(ORDERS_CSV)
    order_items_data = pd.read_csv(ORDER_ITEMS_CSV)

    cur = conn.cursor()
    
    # Customers
    cur.executemany(
        "INSERT INTO customers (customer_name, city) VALUES (?, ?)",
        customers_data[['customer_name', 'city']].values.tolist()
    )

    # Products
    cur.executemany(
        "INSERT INTO products (product_name, unit_price) VALUES (?, ?)",
        products_data[['product_name', 'unit_price']].values.tolist()
    )

    # Stores
    cur.executemany(
        "INSERT INTO stores (store_name, city, manager) VALUES (?, ?, ?)",
        stores_data[['store_name', 'city', 'manager']].values.tolist()
    )

    # Sellers
    cur.executemany(
        "INSERT INTO sellers (seller_name, store_id) VALUES (?, ?)",
        sellers_data[['seller_name', 'store_id']].values.tolist()
    )

    # Orders
    cur.executemany(
        "INSERT INTO orders (customer_id, seller_id, order_date) VALUES (?, ?, ?)",
        orders_data[['customer_id', 'seller_id', 'order_date']].values.tolist()
    )

    # Order items
    cur.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
        order_items_data[['order_id', 'product_id', 'quantity']].values.tolist()
    )

    conn.commit()
    
    print("[" + str(datetime.datetime.now()) + "] — Data inserted successfully.")

# Met à jour les totaux des commandes dans la table orders
def update_order_totals(conn):
    print("[" + str(datetime.datetime.now()) + "] — Updating total amounts in orders table...")
    
    cur = conn.cursor()
    
    cur.execute(
        """
        UPDATE orders
        SET total_amount = subquery.total
        FROM (
            SELECT oi.order_id, SUM(oi.quantity * p.unit_price) AS total
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            GROUP BY oi.order_id
        ) AS subquery
        WHERE orders.order_id = subquery.order_id
        """
    )
    
    conn.commit()
    
    print("[" + str(datetime.datetime.now()) + "] — Order totals updated successfully.")

# Fonction principale pour initialiser la base de données
def main():
    print("[" + str(datetime.datetime.now()) + "] — Initializing the database...")
    conn = db.connect_db()
    
    if conn:
        deleting_tables(conn)
        create_table(conn)
        insert_data(conn)
        update_order_totals(conn)
        conn.close()
    
    print("[" + str(datetime.datetime.now()) + "] — Database initialization completed successfully.")

main()