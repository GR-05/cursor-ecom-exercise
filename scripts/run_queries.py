import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "ecommerce.db"


QUERIES = {
    "orders_with_customers": """
        SELECT o.order_id,
               c.first_name || ' ' || c.last_name AS customer_name,
               o.order_date,
               o.status,
               o.total_amount,
               p.payment_method,
               p.status AS payment_status
        FROM orders o
        JOIN customers c ON o.customer_id = c.customer_id
        LEFT JOIN payments p ON o.order_id = p.order_id
        ORDER BY o.order_date DESC
        LIMIT 10;
    """,
    "top_products_by_revenue": """
        SELECT pr.name,
               pr.category,
               SUM(oi.line_total) AS revenue,
               SUM(oi.quantity) AS units_sold
        FROM order_items oi
        JOIN products pr ON oi.product_id = pr.product_id
        GROUP BY pr.product_id
        ORDER BY revenue DESC
        LIMIT 5;
    """,
    "customer_lifetime_value": """
        SELECT c.customer_id,
               c.first_name || ' ' || c.last_name AS customer_name,
               COUNT(o.order_id) AS total_orders,
               SUM(o.total_amount) AS lifetime_value
        FROM customers c
        JOIN orders o ON o.customer_id = c.customer_id
        GROUP BY c.customer_id
        ORDER BY lifetime_value DESC
        LIMIT 10;
    """,
    "shipments_status": """
        SELECT o.order_id,
               c.first_name || ' ' || c.last_name AS customer_name,
               s.carrier,
               s.tracking_number,
               s.status
        FROM shipments s
        JOIN orders o ON s.order_id = o.order_id
        JOIN customers c ON o.customer_id = c.customer_id
        ORDER BY s.shipped_date DESC
        LIMIT 10;
    """,
}


def run_queries():
    if not DB_PATH.exists():
        raise SystemExit("Database not found. Run load_sqlite.py first.")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    for name, sql in QUERIES.items():
        print(f"\n---- {name} ----")
        cursor.execute(sql)
        rows = cursor.fetchall()
        if not rows:
            print("No results.")
            continue
        headers = rows[0].keys()
        print(" | ".join(headers))
        for row in rows:
            print(" | ".join(str(row[h]) for h in headers))

    conn.close()


if __name__ == "__main__":
    run_queries()

