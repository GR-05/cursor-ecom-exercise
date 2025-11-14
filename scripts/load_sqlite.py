import csv
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "ecommerce.db"


def read_csv(name: str):
    path = DATA_DIR / name
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        yield from reader


def create_schema(cursor: sqlite3.Cursor):
    cursor.executescript(
        """
        PRAGMA foreign_keys = ON;

        DROP TABLE IF EXISTS shipments;
        DROP TABLE IF EXISTS payments;
        DROP TABLE IF EXISTS order_items;
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS customers;

        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            created_at TEXT NOT NULL,
            loyalty_status TEXT NOT NULL
        );

        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            stock_qty INTEGER NOT NULL,
            is_active INTEGER NOT NULL CHECK (is_active IN (0, 1))
        );

        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL,
            total_amount REAL NOT NULL,
            shipping_address TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );

        CREATE TABLE order_items (
            order_item_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            line_total REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );

        CREATE TABLE payments (
            payment_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            payment_date TEXT NOT NULL,
            payment_method TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            transaction_ref TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );

        CREATE TABLE shipments (
            shipment_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            carrier TEXT NOT NULL,
            tracking_number TEXT NOT NULL,
            shipped_date TEXT NOT NULL,
            delivery_estimate TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );
        """
    )


def load_table(cursor: sqlite3.Cursor, table: str, columns: list[str], rows):
    placeholders = ",".join("?" for _ in columns)
    cursor.executemany(
        f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})",
        ([row[col] for col in columns] for row in rows),
    )
    print(f"Loaded {cursor.rowcount} rows into {table}")


def main():
    if not DATA_DIR.exists():
        raise SystemExit("Data directory does not exist. Run generate_data.py first.")

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    create_schema(cursor)

    load_table(
        cursor,
        "customers",
        [
            "customer_id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "created_at",
            "loyalty_status",
        ],
        read_csv("customers.csv"),
    )

    load_table(
        cursor,
        "products",
        ["product_id", "name", "category", "price", "stock_qty", "is_active"],
        read_csv("products.csv"),
    )

    load_table(
        cursor,
        "orders",
        [
            "order_id",
            "customer_id",
            "order_date",
            "status",
            "total_amount",
            "shipping_address",
        ],
        read_csv("orders.csv"),
    )

    load_table(
        cursor,
        "order_items",
        [
            "order_item_id",
            "order_id",
            "product_id",
            "quantity",
            "unit_price",
            "line_total",
        ],
        read_csv("order_items.csv"),
    )

    load_table(
        cursor,
        "payments",
        [
            "payment_id",
            "order_id",
            "payment_date",
            "payment_method",
            "amount",
            "status",
            "transaction_ref",
        ],
        read_csv("payments.csv"),
    )

    load_table(
        cursor,
        "shipments",
        [
            "shipment_id",
            "order_id",
            "carrier",
            "tracking_number",
            "shipped_date",
            "delivery_estimate",
            "status",
        ],
        read_csv("shipments.csv"),
    )

    connection.commit()
    connection.close()
    print(f"Database created at {DB_PATH}")


if __name__ == "__main__":
    main()

