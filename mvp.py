import streamlit as st
import json
from pathlib import Path

st.set_page_config(page_title="MISY350 Groceries", layout="wide")

USER_FILE = Path("users.json")
INVENTORY_FILE = Path("inventory.json")

if not INVENTORY_FILE.exists():
    default_inventory = [
    {"id": 1, "name": "Eggs (1 Dozen)", "price": 2.25, "stock": 22},
    {"id": 2, "name": "Milk (1 Gallon)", "price": 2.99, "stock": 21},
    {"id": 3, "name": "Ground Beef (1 lb)", "price": 7.49, "stock": 20},
    {"id": 4, "name": "Chicken Breast (5 Pack)", "price": 12.99, "stock": 18},
    {"id": 5, "name": "Orange Juice (46 fl oz)", "price": 6.49, "stock": 19},
    {"id": 6, "name": "Apples (3 lb Bag)", "price": 4.99, "stock": 25},
    {"id": 7, "name": "Bananas (1 Bunch)", "price": 1.99, "stock": 30},
    {"id": 8, "name": "Bread (White Loaf)", "price": 3.49, "stock": 16},
    {"id": 9, "name": "Cheddar Cheese (8 oz)", "price": 3.99, "stock": 14},
    {"id": 10, "name": "Bottled Water (24 Pack)", "price": 5.99, "stock": 12},
    {"id": 11, "name": "Greek Yogurt (32 oz)", "price": 4.79, "stock": 17},
    {"id": 12, "name": "Cereal (Family Size)", "price": 4.99, "stock": 15},
]
    INVENTORY_FILE.write_text(json.dumps(default_inventory, indent=4))

if not USER_FILE.exists():
    USER_FILE.write_text(json.dumps([], indent=4))


def load_users():
    return json.loads(USER_FILE.read_text())


def save_users(users):
    USER_FILE.write_text(json.dumps(users, indent=4))


def load_inventory():
    return json.loads(INVENTORY_FILE.read_text())


def save_inventory(data):
    INVENTORY_FILE.write_text(json.dumps(data, indent=4))


if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None


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


def add_style():
    st.markdown("""
        <style>
        .main-title {
            font-size: 46px;
            font-weight: 800;
            color: #2E8B57;
            text-align: center;
            margin-bottom: 5px;
        }

        .sub-title {
            font-size: 20px;
            color: #555;
            text-align: center;
            margin-bottom: 30px;
        }

        .welcome-box {
            background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
            padding: 25px;
            border-radius: 18px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0px 4px 14px rgba(0,0,0,0.12);
        }

        .welcome-box h3 {
            color: #1b5e20;
        }
        </style>
    """, unsafe_allow_html=True)


def welcome_header(user):
    st.markdown("""
        <div class="main-title">🛒 Welcome to MISY350 Groceries</div>
        <div class="sub-title">Fresh inventory. Simple orders. Smarter grocery management.</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="welcome-box">
            <h3>Welcome, {user['username']}!</h3>
            <p>You are logged in as <strong>{user['role']}</strong>.</p>
        </div>
    """, unsafe_allow_html=True)


def page_inventory():
    inventory = load_inventory()

    st.header("Admin Inventory Manager")
    st.write("Admins can view and update grocery inventory.")

    search_query = st.text_input(
        "Search by item name",
        placeholder="e.g. Milk"
    )

    filtered = [
        item for item in inventory
        if search_query.lower() in item["name"].lower()
    ]

    total_stock = sum(item["stock"] for item in inventory)
    low_stock_count = sum(1 for item in inventory if item["stock"] < 20)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Items", len(inventory))
    col2.metric("Units in Stock", total_stock)
    col3.metric("Low Stock Items", low_stock_count)

    st.markdown("---")

    for item in filtered:
        col_a, col_b, col_c, col_d, col_e = st.columns([3, 2, 2, 2, 1])

        col_a.write(f"**{item['name']}**")
        col_b.write(f"ID: `{item['id']}`")

        new_price = col_c.number_input(
            "Price ($)",
            min_value=0.0,
            value=float(item["price"]),
            step=0.01,
            format="%.2f",
            key=f"price_{item['id']}"
        )

        new_stock = col_d.number_input(
            "Stock",
            min_value=0,
            value=int(item["stock"]),
            step=1,
            key=f"stock_{item['id']}"
        )

        if item["stock"] < 20:
            col_d.caption("⚠️ Low stock")

        if col_e.button("Save", key=f"save_{item['id']}"):
            item["price"] = round(new_price, 2)
            item["stock"] = int(new_stock)
            save_inventory(inventory)
            st.success(f"{item['name']} updated.")
            st.rerun()

        st.divider()


def page_orders():
    inventory = load_inventory()

    st.header("Place Grocery Order")
    st.write("Users can only place orders from available inventory.")

    customer = st.text_input("Customer Name")

    product_names = [
        item["name"] for item in inventory
        if item["stock"] > 0
    ]

    if not product_names:
        st.warning("No items are currently in stock.")
        return

    selected_product = st.selectbox("Select Product", product_names)

    product = None
    for item in inventory:
        if item["name"] == selected_product:
            product = item
            break

    if product:
        st.info(f"Available Stock: {product['stock']} | Price: ${product['price']:.2f}")

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            max_value=int(product["stock"]),
            step=1
        )

        total = quantity * product["price"]
        st.success(f"Total: ${total:.2f}")

        if st.button("Submit Order"):
            if customer.strip() == "":
                st.error("Please enter a customer name.")
            else:
                product["stock"] -= int(quantity)
                save_inventory(inventory)

                st.success("Order placed successfully! Inventory has been updated.")
                st.rerun()


add_style()

if not st.session_state.logged_in:
    st.markdown("""
        <div class="main-title">🛒 MISY350 Groceries</div>
        <div class="sub-title">Login or register to continue.</div>
    """, unsafe_allow_html=True)

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
        role = st.selectbox("Select Role", ["user", "admin"])

        if st.button("Register"):
            if new_user.strip() == "" or new_pass.strip() == "":
                st.error("Please enter both username and password.")
            else:
                success, message = register(new_user, new_pass, role)

                if success:
                    st.success(message)
                else:
                    st.error(message)

else:
    user = st.session_state.user

    welcome_header(user)

    st.sidebar.title(f"Welcome, {user['username']}")

    page = st.sidebar.radio(
        "Navigation",
        ["Dashboard", "Profile", "Logout"]
    )

    if page == "Dashboard":
        if user["role"] == "admin":
            page_inventory()
        elif user["role"] == "user":
            page_orders()

    elif page == "Profile":
        st.header("Profile")
        st.write(f"Username: {user['username']}")
        st.write(f"Role: {user['role']}")

    elif page == "Logout":
        st.session_state.logged_in = False
        st.session_state.user = None
        st.success("Logged out")
        st.rerun()
