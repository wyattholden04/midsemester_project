import json
from pathlib import Path

USER_FILE = Path("users.json")
INVENTORY_FILE = Path("inventory.project.json")
ORDERS_FILE = Path("orders.json")

if not USER_FILE.exists():
    USER_FILE.write_text(json.dumps([], indent=4))

if not ORDERS_FILE.exists():
    ORDERS_FILE.write_text(json.dumps([], indent=4))


def load_users():
    return json.loads(USER_FILE.read_text())


def save_users(users):
    USER_FILE.write_text(json.dumps(users, indent=4))


def load_inventory():
    return json.loads(INVENTORY_FILE.read_text())


def save_inventory(data):
    INVENTORY_FILE.write_text(json.dumps(data, indent=4))


def load_orders():
    return json.loads(ORDERS_FILE.read_text())


def save_orders(data):
    ORDERS_FILE.write_text(json.dumps(data, indent=4))
