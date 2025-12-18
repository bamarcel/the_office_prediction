import psycopg as pg
import datetime

CONNECTION_STRING = "postgresql://postgres:root@localhost:5432/the_office"

def connect_db():
    try:
        conn = pg.connect(CONNECTION_STRING)
        print("[" + str(datetime.datetime.now()) + "] — Connection to the database was successful.")
        return conn
    except Exception as e:
        print(f"[" + str(datetime.datetime.now()) + "] — An error occurred while connecting to the database: {e}")
        return None