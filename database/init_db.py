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
    
    try:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS order_items")
            cur.execute("DROP TABLE IF EXISTS orders")
            cur.execute("DROP TABLE IF EXISTS sellers")
            cur.execute("DROP TABLE IF EXISTS stores")
            cur.execute("DROP TABLE IF EXISTS products")
            cur.execute("DROP TABLE IF EXISTS customers")
        conn.commit()
        print("[" + str(datetime.datetime.now()) + "] — Existing tables deleted.")
    except Exception as e:
        print(f"[" + str(datetime.datetime.now()) + "] — An error occurred while deleting tables: {e}")
        return

# Crée les tables nécessaires
def create_table(conn):
    print("[" + str(datetime.datetime.now()) + "] — Creating tables in the database...")
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id SERIAL PRIMARY KEY,
                    customer_name VARCHAR(100),
                    city VARCHAR(100)
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS products (
                    product_id SERIAL PRIMARY KEY,
                    product_name VARCHAR(100),
                    unit_price DECIMAL
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS stores (
                    store_id SERIAL PRIMARY KEY,
                    store_name VARCHAR(100),
                    city VARCHAR(100),
                    manager VARCHAR(100)
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS sellers (
                    seller_id SERIAL PRIMARY KEY,
                    seller_name VARCHAR(100),
                    store_id INT REFERENCES stores(store_id)
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS orders (
                    order_id SERIAL PRIMARY KEY,
                    customer_id INT REFERENCES customers(customer_id),
                    seller_id INT REFERENCES sellers(seller_id),
                    order_date DATE,
                    total_amount DECIMAL DEFAULT 0
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS order_items (
                    order_item_id SERIAL PRIMARY KEY,
                    order_id INT REFERENCES orders(order_id),
                    product_id INT REFERENCES products(product_id),
                    quantity INT
                )
                """
            )

        conn.commit()
        print("[" + str(datetime.datetime.now()) + "] — Tables created successfully.")
    except Exception as e:
        print(f"[" + str(datetime.datetime.now()) + "] — An error occurred while creating tables: {e}")
        return

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

    try:
        with conn.cursor() as cur:
            # Customers
            cur.executemany(
                "INSERT INTO customers (customer_name, city) VALUES (%s, %s)",
                customers_data[['customer_name', 'city']].values.tolist()
            )

            # Products
            cur.executemany(
                "INSERT INTO products (product_name, unit_price) VALUES (%s, %s)",
                products_data[['product_name', 'unit_price']].values.tolist()
            )

            # Stores
            cur.executemany(
                "INSERT INTO stores (store_name, city, manager) VALUES (%s, %s, %s)",
                stores_data[['store_name', 'city', 'manager']].values.tolist()
            )

            # Sellers
            cur.executemany(
                "INSERT INTO sellers (seller_name, store_id) VALUES (%s, %s)",
                sellers_data[['seller_name', 'store_id']].values.tolist()
            )

            # Orders
            cur.executemany(
                "INSERT INTO orders (customer_id, seller_id, order_date) VALUES (%s, %s, %s)",
                orders_data[['customer_id', 'seller_id', 'order_date']].values.tolist()
            )

            # Order items
            cur.executemany(
                "INSERT INTO order_items (order_id, product_id, quantity) VALUES (%s, %s, %s)",
                order_items_data[['order_id', 'product_id', 'quantity']].values.tolist()
            )

        conn.commit()
        print("[" + str(datetime.datetime.now()) + "] — Data inserted successfully.")
    except Exception as e:
        print(f"[" + str(datetime.datetime.now()) + "] — An error occurred while inserting data: {e}")
        conn.rollback()


# Met à jour les totaux des commandes dans la table orders
def update_order_totals(conn):
    print("[" + str(datetime.datetime.now()) + "] — Updating total amounts in orders table...")
    try:
        with conn.cursor() as cur:
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
    except Exception as e:
        print(f"[" + str(datetime.datetime.now()) + "] — An error occurred while updating order totals: {e}")
        return

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

try:
    main()
except Exception as e:
    print(f"[" + str(datetime.datetime.now()) + "] — An unexpected error occurred: {e}")