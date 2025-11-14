# cursor-ecom-exercise
This project generates realistic synthetic e-commerce datasets, automated SQLite database creation, and demonstrates analytical SQL joins across tables. Built entirely in Cursor IDE to demonstrate data generation, ingestion, and query workflows in a simple end-to-end pipeline.

## Project Structure

- `scripts/generate_data.py` – creates CSV files for each table.
- `scripts/load_sqlite.py` – builds `ecommerce.db` and loads the CSV data.
- `scripts/run_queries.py` – runs sample JOIN queries and prints the results.
- `data/` – output folder for generated CSV files.

## Quickstart

1. **Install dependencies**
   ```bash
   python -m pip install -r requirements.txt
   ```

2. **Generate synthetic CSVs**
   ```bash
   python scripts/generate_data.py
   ```

3. **Load CSVs into SQLite**
   ```bash
   python scripts/load_sqlite.py
   ```

4. **Run example JOIN queries**
   ```bash
   python scripts/run_queries.py
   ```

The SQLite database file `ecommerce.db` will be created in the project root, along with CSV exports inside `data/`.

## Schema Overview

- `customers` ← primary key `customer_id`
- `products` ← primary key `product_id`
- `orders` ← references `customers.customer_id`
- `order_items` ← references `orders.order_id` and `products.product_id`
- `payments` ← references `orders.order_id`
- `shipments` ← references `orders.order_id`
