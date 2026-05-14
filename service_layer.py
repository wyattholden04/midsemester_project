from datetime import datetime
from data_layer import load_users, save_users, load_orders, save_orders


def register(username, password, role):
    users = load_users()

    for user in users:
        if user["username"] == username:
            return False, "Username already exists"

    users.append({
        "username": username,
        "password": password,
        "role": role
    })

    save_users(users)
    return True, "Account created successfully"


def login(username, password):
    users = load_users()

    for user in users:
        if user["username"] == username and user["password"] == password:
            return True, user

    return False, None


def add_to_cart(cart, product, quantity):
    for cart_item in cart:
        if cart_item["id"] == product["id"]:
            new_quantity = cart_item["quantity"] + int(quantity)

            if new_quantity > product["stock"]:
                return cart, False, "You cannot add more than the available stock."

            cart_item["quantity"] = new_quantity
            cart_item["total"] = round(cart_item["quantity"] * cart_item["price"], 2)

            return cart, True, f"{product['name']} quantity updated in cart."

    cart.append({
        "id": product["id"],
        "name": product["name"],
        "category": product.get("category", "Other"),
        "price": product["price"],
        "quantity": int(quantity),
        "total": round(quantity * product["price"], 2)
    })

    return cart, True, f"{product['name']} added to cart."


def add_to_favorites(favorites, product):
    for favorite in favorites:
        if favorite["id"] == product["id"]:
            return favorites, False, f"{product['name']} is already in your favorites."

    favorites.append({
        "id": product["id"],
        "name": product["name"],
        "category": product.get("category", "Other"),
        "price": product["price"],
        "stock": product["stock"],
        "image": product.get("image", "")
    })

    return favorites, True, f"{product['name']} added to favorites."


def remove_from_favorites(favorites, product_id):
    updated_favorites = [
        item for item in favorites
        if item["id"] != product_id
    ]

    return updated_favorites


def save_customer_order(cart, customer, total):
    orders = load_orders()

    next_order_id = 1
    if orders:
        next_order_id = max(order.get("order_id", 0) for order in orders) + 1

    order = {
        "order_id": next_order_id,
        "customer": customer,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "items": cart,
        "total": round(total, 2),
        "status": "Placed"
    }

    orders.append(order)
    save_orders(orders)

    return order


def calculate_cart_total(cart):
    return sum(item["total"] for item in cart)


def calculate_total_items(cart):
    return sum(item["quantity"] for item in cart)
