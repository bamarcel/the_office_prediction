import datetime
from database.connect_db import connect_db


def run_query(query, params=None, fetch="all"):
    """
    Exécute une requête SQL et retourne les résultats.
    - fetch="all"  → liste de tuples
    - fetch="one"  → un seul tuple ou None
    """
    conn = connect_db()
    if not conn:
        print(f"[{datetime.datetime.now()}] — DB connection failed")
        return None

    try:
        cur = conn.cursor()
        cur.execute(query, params or ())

        if fetch == "one":
            return cur.fetchone()
        return cur.fetchall()

    except Exception as e:
        print(f"[{datetime.datetime.now()}] — SQL Error: {e}")
        return None

    finally:
        conn.close()
