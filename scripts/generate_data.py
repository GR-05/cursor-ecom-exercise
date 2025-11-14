import csv
import random
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker


fake = Faker()
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


@dataclass
class Customer:
    customer_id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    created_at: str
    loyalty_status: str


@dataclass
class Product:
    product_id: int
    name: str
    category: str
    price: float
    stock_qty: int
    is_active: int


@dataclass
class Order:
    order_id: int
    customer_id: int
    order_date: str
    status: str
    total_amount: float
    shipping_address: str


@dataclass
class OrderItem:
    order_item_id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: float
    line_total: float


@dataclass
class Payment:
    payment_id: int
    order_id: int
    payment_date: str
    payment_method: str
    amount: float
    status: str
    transaction_ref: str


@dataclass
class Shipment:
    shipment_id: int
    order_id: int
    carrier: str
    tracking_number: str
    shipped_date: str
    delivery_estimate: str
    status: str


def write_csv(filename: str, rows):
    fieldnames = rows[0].keys()
    path = DATA_DIR / filename
    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {path}")


def generate_customers(count: int) -> list[Customer]:
    tiers = ["bronze", "silver", "gold", "platinum"]
    customers = []
    for idx in range(1, count + 1):
        first_name = fake.first_name()
        last_name = fake.last_name()
        created_at = fake.date_time_between(start_date="-2y", end_date="now")
        customers.append(
            Customer(
                customer_id=idx,
                first_name=first_name,
                last_name=last_name,
                email=f"{first_name.lower()}.{last_name.lower()}{idx}@example.com",
                phone=fake.msisdn()[:10],
                created_at=created_at.isoformat(),
                loyalty_status=random.choices(tiers, weights=[0.5, 0.3, 0.15, 0.05])[0],
            )
        )
    return customers


def generate_products(count: int) -> list[Product]:
    categories = [
        "Apparel",
        "Electronics",
        "Home & Kitchen",
        "Beauty",
        "Outdoors",
        "Toys",
    ]
    products = []
    for idx in range(1, count + 1):
        category = random.choice(categories)
        price = round(random.uniform(5, 500), 2)
        products.append(
            Product(
                product_id=idx,
                name=f"{fake.color_name()} {category} Item {idx}",
                category=category,
                price=price,
                stock_qty=random.randint(10, 500),
                is_active=random.choice([0, 1]),
            )
        )
    return products


def generate_orders(customers: list[Customer], count: int) -> list[Order]:
    statuses = ["processing", "completed", "cancelled", "refunded"]
    orders = []
    for idx in range(1, count + 1):
        customer = random.choice(customers)
        order_date = fake.date_time_between(start_date="-1y", end_date="now")
        orders.append(
            Order(
                order_id=idx,
                customer_id=customer.customer_id,
                order_date=order_date.isoformat(),
                status=random.choices(statuses, weights=[0.5, 0.35, 0.1, 0.05])[0],
                total_amount=0.0,  # placeholder, set later
                shipping_address=fake.address().replace("\n", ", "),
            )
        )
    return orders


def generate_order_items(
    orders: list[Order], products: list[Product], max_items_per_order: int = 5
) -> list[OrderItem]:
    order_items: list[OrderItem] = []
    order_item_id = 1
    for order in orders:
        num_items = random.randint(1, max_items_per_order)
        selected_products = random.sample(products, k=num_items)
        total = 0.0
        for product in selected_products:
            quantity = random.randint(1, 4)
            unit_price = product.price * random.uniform(0.9, 1.1)
            line_total = round(quantity * unit_price, 2)
            total += line_total
            order_items.append(
                OrderItem(
                    order_item_id=order_item_id,
                    order_id=order.order_id,
                    product_id=product.product_id,
                    quantity=quantity,
                    unit_price=round(unit_price, 2),
                    line_total=line_total,
                )
            )
            order_item_id += 1
        order.total_amount = round(total, 2)
    return order_items


def generate_payments(orders: list[Order]) -> list[Payment]:
    methods = ["credit_card", "paypal", "bank_transfer", "gift_card"]
    payment_statuses = ["captured", "pending", "failed", "refunded"]
    payments = []
    for order in orders:
        payment_date = datetime.fromisoformat(order.order_date) + timedelta(
            hours=random.randint(1, 72)
        )
        status = (
            "refunded"
            if order.status == "refunded"
            else random.choices(payment_statuses, weights=[0.7, 0.2, 0.05, 0.05])[0]
        )
        payments.append(
            Payment(
                payment_id=order.order_id,
                order_id=order.order_id,
                payment_date=payment_date.isoformat(),
                payment_method=random.choice(methods),
                amount=order.total_amount,
                status=status,
                transaction_ref=f"TXN-{order.order_id:05d}",
            )
        )
    return payments


def generate_shipments(orders: list[Order]) -> list[Shipment]:
    carriers = ["DHL", "FedEx", "UPS", "USPS", "Royal Mail"]
    statuses = ["label_created", "in_transit", "delivered", "delayed"]
    shipments = []
    for order in orders:
        if order.status in {"cancelled", "refunded"}:
            continue
        order_date = datetime.fromisoformat(order.order_date)
        shipped_date = order_date + timedelta(days=random.randint(1, 5))
        delivery_estimate = shipped_date + timedelta(days=random.randint(2, 7))
        shipments.append(
            Shipment(
                shipment_id=len(shipments) + 1,
                order_id=order.order_id,
                carrier=random.choice(carriers),
                tracking_number=fake.bothify(text="??########"),
                shipped_date=shipped_date.isoformat(),
                delivery_estimate=delivery_estimate.isoformat(),
                status=random.choice(statuses),
            )
        )
    return shipments


def main():
    DATA_DIR.mkdir(exist_ok=True)
    customers = generate_customers(120)
    products = generate_products(60)
    orders = generate_orders(customers, 300)
    order_items = generate_order_items(orders, products)
    payments = generate_payments(orders)
    shipments = generate_shipments(orders)

    write_csv("customers.csv", [asdict(c) for c in customers])
    write_csv("products.csv", [asdict(p) for p in products])
    write_csv("orders.csv", [asdict(o) for o in orders])
    write_csv("order_items.csv", [asdict(oi) for oi in order_items])
    write_csv("payments.csv", [asdict(p) for p in payments])
    write_csv("shipments.csv", [asdict(s) for s in shipments])


if __name__ == "__main__":
    main()

