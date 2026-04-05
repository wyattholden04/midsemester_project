import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="Orders", layout="wide")

USER_FILE      = Path("users.json")
INVENTORY_FILE = Path("inventory.json")

if not INVENTORY_FILE.exists():
    default_inventory = [
        {"id": 1, "name": "Eggs (1 Dozen)",         "price": 2.25,  "stock": 22},
        {"id": 2, "name": "Milk (1 Gallon)",         "price": 2.99,  "stock": 21},
        {"id": 3, "name": "Ground Beef (1 lb)",      "price": 7.49,  "stock": 20},
        {"id": 4, "name": "Chicken Breast (5 Pack)", "price": 12.99, "stock": 18},
        {"id": 5, "name": "Orange Juice (46 fl oz)", "price": 6.49,  "stock": 19},
    ]
    INVENTORY_FILE.write_text(json.dumps(default_inventory, indent=4))

if not USER_FILE.exists():
    with open(USER_FILE, "w") as f:
        json.dump([], f)

def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None

def register(username, password, role):
    users = load_users()
    for user in users:
        if user["username"] == username:
            return False, "Username already exists"
    users.append({"username": username, "password": password, "role": role})
    save_users(users)
    return True, "Account created successfully"

def login(username, password):
    users = load_users()
    for user in users:
        if user["username"] == username and user["password"] == password:
            return True, user
    return False, None

def load_inventory():
    if not INVENTORY_FILE.exists():
        return []
    try:
        data = json.loads(INVENTORY_FILE.read_text())
        if not isinstance(data, list):
            raise ValueError("inventory data is not a list")
        return data
    except Exception:
        return []

def save_inventory(data):
    INVENTORY_FILE.write_text(json.dumps(data, indent=4))

def page_inventory():
    if "inventory" not in st.session_state:
        st.session_state.inventory = load_inventory()

    st.title("Inventory Manager")
    st.header("View & Adjust Inventory")

    inventory = st.session_state.inventory

    search_query = st.text_input("Search by item name", placeholder="e.g. Milk", key="search")

    filtered = [
        i for i in inventory
        if search_query.lower() in i["name"].lower()
    ]

    total_stock = sum(i.get("stock", 0) for i in inventory)
    low_stock_count = sum(1 for i in inventory if i.get("stock", 0) < 20)

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Items in Catalogue", len(inventory))
    m2.metric("Total Units in Stock", total_stock)
    m3.metric("Low Stock Items", low_stock_count)

    st.markdown("---")

    if not filtered:
        st.warning("No items match your search.")
    else:
        for item in filtered:
            col_a, col_b, col_c, col_d, col_e = st.columns([3, 2, 2, 2, 1])

            col_a.write(f"**{item['name']}**")
            col_b.write(f"ID: `{item['id']}`")

            new_price = col_c.number_input(
                "Price ($)",
                min_value=0.0,
                max_value=9999.0,
                value=item.get("price", 0.0),
                step=0.01,
                format="%.2f",
                key=f"price_{item['id']}"
            )

            new_stock = col_d.number_input(
                "Stock",
                min_value=0,
                max_value=9999,
                value=item.get("stock", 0),
                step=1,
                key=f"stock_{item['id']}"
            )

            if item.get("stock", 0) < 20:
                col_d.caption("⚠️ Low stock")

            if col_e.button("Save", key=f"save_{item['id']}"):
                item["price"] = new_price
                item["stock"] = new_stock
                save_inventory(inventory)
                st.success(f"✅ '{item['name']}' updated.")
                st.rerun()

            st.divider()


def page_orders():
    inventory = load_inventory()

    if "orders" not in st.session_state:
        st.session_state.orders = [
            {"order_id": 1, "customer": "Matt",  "item": "Eggs (1 Dozen)",    "quantity": 2, "total": 4.50,  "status": "Placed"},
            {"order_id": 2, "customer": "Sarah", "item": "Milk (1 Gallon)",   "quantity": 1, "total": 2.99,  "status": "Completed"},
            {"order_id": 3, "customer": "Jake",  "item": "Ground Beef (1 lb)","quantity": 3, "total": 22.47, "status": "Placed"}
        ]

    if "next_order_id" not in st.session_state:
        st.session_state.next_order_id = 4

    def get_product(product_name):
        for product in inventory:
            if product["name"] == product_name:
                return product
        return None

    st.title("Orders")

    tab1, tab2 = st.tabs(["Orders", "Place Order"])

    with tab1:
        st.subheader("Order List")

        df_orders = pd.DataFrame(st.session_state.orders)

        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Placed", "Completed", "Cancelled"]
        )

        if status_filter != "All":
            df_orders = df_orders[df_orders["status"] == status_filter]

        st.dataframe(df_orders, use_container_width=True)

    with tab2:
        st.subheader("Place Order")

        customer = st.text_input("Customer Name")
        product_names = [product["name"] for product in inventory]
        selected_product = st.selectbox("Select Product", product_names)

        product = get_product(selected_product)

        if product:
            quantity = st.number_input(
                "Quantity",
                min_value=1,
                max_value=product["stock"],
                step=1
            )

            total = quantity * product["price"]
            st.write(f"Total: ${total:.2f}")

            if st.button("Submit Order"):
                if customer.strip() == "":
                    st.error("Please enter a customer name.")
                else:
                    st.session_state.orders.append({
                        "order_id": st.session_state.next_order_id,
                        "customer": customer,
                        "item": selected_product,
                        "quantity": int(quantity),
                        "total": round(total, 2),
                        "status": "Placed"
                    })

                    st.session_state.next_order_id += 1
                    st.success("Order placed successfully!")
                    st.rerun()


if not st.session_state.logged_in:
    st.title(" Login System")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            success, user = login(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success("Logged in successfully")
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        st.subheader("Register")
        new_user = st.text_input("Create Username")
        new_pass = st.text_input("Create Password", type="password")
        role = st.selectbox("Select Role", ["user", "orders"])

        if st.button("Register"):
            success, message = register(new_user, new_pass, role)
            if success:
                st.success(message)
            else:
                st.error(message)

else:
    user = st.session_state.user

    st.sidebar.title(f"Welcome, {user['username']}")

    page = st.sidebar.radio("Navigation", ["Dashboard", "Profile", "Settings", "Logout"])

    if page == "Dashboard":
        if user["role"] == "user":
            page_inventory()
        elif user["role"] == "orders":
            page_orders()

    elif page == "Profile":
        st.title(" Profile")
        st.write(f"Username: {user['username']}")
        st.write(f"Role: {user['role']}")

    elif page == "Settings":
        st.title(" Settings")
        st.write("Settings page (you can expand this)")

    elif page == "Logout":
        st.session_state.logged_in = False
        st.session_state.user = None
        st.success("Logged out")
        st.rerun()
