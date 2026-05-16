import pandas as pd
import pathlib
import datetime

import database.connect_db as db

ABSOLUT_PATH = pathlib.Path(__file__).parent

CUSTOMERS_CSV   = ABSOLUT_PATH / ".." / "data" / "customers.csv"
PRODUCTS_CSV    = ABSOLUT_PATH / ".." / "data" / "products.csv"
STORES_CSV      = ABSOLUT_PATH / ".." / "data" / "stores.csv"
SELLERS_CSV     = ABSOLUT_PATH / ".." / "data" / "sellers.csv"
ORDERS_CSV      = ABSOLUT_PATH / ".." / "data" / "orders.csv"
ORDER_ITEMS_CSV = ABSOLUT_PATH / ".." / "data" / "order_items.csv"


def deleting_tables(conn):
    print(f"[{datetime.datetime.now()}] — Deleting existing tables...")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS order_items")
    cur.execute("DROP TABLE IF EXISTS orders")
    cur.execute("DROP TABLE IF EXISTS sellers")
    cur.execute("DROP TABLE IF EXISTS stores")
    cur.execute("DROP TABLE IF EXISTS products")
    cur.execute("DROP TABLE IF EXISTS customers")
    conn.commit()
    print(f"[{datetime.datetime.now()}] — Existing tables deleted.")


def create_table(conn):
    print(f"[{datetime.datetime.now()}] — Creating tables...")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE customers (
            customer_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            city          TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE products (
            product_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            unit_price   REAL
        )
    """)
    cur.execute("""
        CREATE TABLE stores (
            store_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            store_name TEXT,
            city       TEXT,
            manager    TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE sellers (
            seller_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            seller_name TEXT,
            store_id    INTEGER,
            FOREIGN KEY (store_id) REFERENCES stores(store_id)
        )
    """)
    cur.execute("""
        CREATE TABLE orders (
            order_id     INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id  INTEGER,
            seller_id    INTEGER,
            order_date   TEXT,
            total_amount REAL DEFAULT 0,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
            FOREIGN KEY (seller_id)   REFERENCES sellers(seller_id)
        )
    """)
    cur.execute("""
        CREATE TABLE order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id      INTEGER,
            product_id    INTEGER,
            quantity      INTEGER,
            FOREIGN KEY (order_id)   REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        )
    """)
    conn.commit()
    print(f"[{datetime.datetime.now()}] — Tables created successfully.")


def insert_data(conn):
    print(f"[{datetime.datetime.now()}] — Inserting data...")
    cur = conn.cursor()

    customers_data   = pd.read_csv(CUSTOMERS_CSV)
    products_data    = pd.read_csv(PRODUCTS_CSV)
    stores_data      = pd.read_csv(STORES_CSV)
    sellers_data     = pd.read_csv(SELLERS_CSV)
    orders_data      = pd.read_csv(ORDERS_CSV)
    order_items_data = pd.read_csv(ORDER_ITEMS_CSV)

    cur.executemany(
        "INSERT INTO customers (customer_name, city) VALUES (?, ?)",
        customers_data[['customer_name', 'city']].values.tolist()
    )
    cur.executemany(
        "INSERT INTO products (product_name, unit_price) VALUES (?, ?)",
        products_data[['product_name', 'unit_price']].values.tolist()
    )
    cur.executemany(
        "INSERT INTO stores (store_name, city, manager) VALUES (?, ?, ?)",
        stores_data[['store_name', 'city', 'manager']].values.tolist()
    )
    cur.executemany(
        "INSERT INTO sellers (seller_name, store_id) VALUES (?, ?)",
        sellers_data[['seller_name', 'store_id']].values.tolist()
    )
    cur.executemany(
        "INSERT INTO orders (customer_id, seller_id, order_date) VALUES (?, ?, ?)",
        orders_data[['customer_id', 'seller_id', 'order_date']].values.tolist()
    )
    cur.executemany(
        "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
        order_items_data[['order_id', 'product_id', 'quantity']].values.tolist()
    )
    conn.commit()
    print(f"[{datetime.datetime.now()}] — Data inserted successfully.")


def update_order_totals(conn):
    """
    Calcule et met à jour total_amount pour chaque commande.
    Utilise la syntaxe SQLite correcte (sous-requête corrélée),
    contrairement à UPDATE...FROM qui est spécifique à PostgreSQL.
    """
    print(f"[{datetime.datetime.now()}] — Updating order totals...")
    cur = conn.cursor()

    cur.execute("""
        UPDATE orders
        SET total_amount = (
            SELECT COALESCE(SUM(oi.quantity * p.unit_price), 0)
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            WHERE oi.order_id = orders.order_id
        )
    """)
    conn.commit()
    print(f"[{datetime.datetime.now()}] — Order totals updated successfully.")


def main():
    print(f"[{datetime.datetime.now()}] — Initializing the database...")
    conn = db.connect_db()

    if not conn:
        print(f"[{datetime.datetime.now()}] — Cannot connect to DB. Aborting.")
        return

    deleting_tables(conn)
    create_table(conn)
    insert_data(conn)
    update_order_totals(conn)
    conn.close()

    print(f"[{datetime.datetime.now()}] — Database initialization completed.")


if __name__ == "__main__":
    main()
