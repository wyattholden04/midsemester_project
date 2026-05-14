import streamlit as st
from pathlib import Path

from data_layer import (
    load_inventory,
    save_inventory,
    load_orders,
    load_users,
    save_users,
)

from service_layer import (
    register,
    login,
    add_to_cart,
    add_to_favorites,
    remove_from_favorites,
    save_customer_order,
    calculate_cart_total,
    calculate_total_items,
)

from ai_assistant import get_ai_response


CATEGORY_ICONS = {
    "Dairy & Eggs": "🥛",
    "Meat": "🥩",
    "Drinks": "🥤",
    "Produce": "🍎",
    "Bakery": "🍞",
    "Pantry": "🥫",
    "Other": "🛒"
}


def add_style():
    st.markdown("""
        <style>
        .main-title {
            font-size: 50px;
            font-weight: 900;
            color: #2E8B57;
            text-align: center;
            margin-bottom: 5px;
        }

        .sub-title {
            font-size: 20px;
            color: #555;
            text-align: center;
            margin-bottom: 28px;
        }

        .welcome-box {
            background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
            padding: 24px;
            border-radius: 18px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0px 4px 14px rgba(0,0,0,0.12);
        }

        .welcome-box h3 {
            color: #1b5e20;
            margin-bottom: 5px;
        }

        .product-card {
            background: linear-gradient(145deg, #ffffff, #f8fdf8);
            padding: 18px;
            border-radius: 18px;
            border: 2px solid #d9f2dc;
            box-shadow: 0px 4px 14px rgba(0,0,0,0.08);
            margin-bottom: 16px;
        }

        .product-name {
            font-size: 20px;
            font-weight: 700;
            color: #1b5e20;
            margin-bottom: 8px;
        }

        .product-divider {
            height: 3px;
            background: linear-gradient(to right, #2E8B57, #90EE90);
            border-radius: 10px;
            margin-top: 12px;
        }

        .footer {
            text-align: center;
            color: #777;
            margin-top: 45px;
            padding-top: 20px;
            border-top: 1px solid #eeeeee;
            font-size: 14px;
        }
        </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "user" not in st.session_state:
        st.session_state.user = None

    if "cart" not in st.session_state:
        st.session_state.cart = []

    if "favorites" not in st.session_state:
        st.session_state.favorites = []


def welcome_header(user):
    st.markdown("""
        <div class="main-title">🛒 Welcome to MISY350 Groceries</div>
        <div class="sub-title">Your campus grocery management system</div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
        <div class="welcome-box">
            <h3>Welcome, {user['username']}!</h3>
            <p>System Status: <strong>Active</strong> | Access Type: <strong>{user['role']}</strong></p>
        </div>
    """, unsafe_allow_html=True)


def sidebar_info(user):
    st.sidebar.title("🛒 MISY350 Groceries")
    st.sidebar.write(f"Logged in as: **{user['username']}**")
    st.sidebar.write(f"Role: **{user['role']}**")
    st.sidebar.divider()

    if user["role"] == "admin":
        st.sidebar.info("Admin tools: Inventory, Orders, AI Assistant")
    else:
        st.sidebar.info("User tools: Shop, Favorites, Cart, AI Assistant")

    st.sidebar.divider()
    st.sidebar.write("Built for MISY350")


def footer():
    st.markdown("""
        <div class="footer">
            MISY350 Groceries © 2026 | Built with Streamlit
        </div>
    """, unsafe_allow_html=True)


def product_header_card(name, icon=""):
    st.markdown(f"""
        <div class="product-card">
            <div class="product-name">{icon} {name}</div>
            <div class="product-divider"></div>
        </div>
    """, unsafe_allow_html=True)


def show_product_image(image_path):
    if image_path:
        full_image_path = Path(".devcontainer") / image_path

        if full_image_path.exists():
            st.image(str(full_image_path), width=220)
        else:
            st.warning(f"Missing image: {image_path}")


def page_inventory():
    inventory = load_inventory()

    st.header("📦 Admin Inventory Manager")

    categories = ["All"] + sorted(
        set(item.get("category", "Other") for item in inventory)
    )

    selected_category = st.selectbox("Filter by Category", categories)
    search_query = st.text_input("Search Inventory", placeholder="Search items...")

    filtered = [
        item for item in inventory
        if search_query.lower() in item["name"].lower()
        and (
            selected_category == "All"
            or item.get("category", "Other") == selected_category
        )
    ]

    total_stock = sum(item["stock"] for item in inventory)
    low_stock_count = sum(1 for item in inventory if item["stock"] < 20)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Products", len(inventory))
    col2.metric("Units in Stock", total_stock)
    col3.metric("Low Stock Items", low_stock_count)

    st.markdown("---")

    if not filtered:
        st.warning("No items found.")
        return

    for item in filtered:
        icon = CATEGORY_ICONS.get(item.get("category", "Other"), "🛒")

        product_header_card(item["name"], icon)

        show_product_image(item.get("image"))

        st.divider()

        st.write(f"Category: **{item.get('category', 'Other')}**")
        st.write(f"Product ID: `{item['id']}`")

        col1, col2, col3 = st.columns([2, 2, 1])

        new_price = col1.number_input(
            "Price ($)",
            min_value=0.0,
            value=float(item["price"]),
            step=0.01,
            format="%.2f",
            key=f"price_{item['id']}"
        )

        new_stock = col2.number_input(
            "Stock",
            min_value=0,
            value=int(item["stock"]),
            step=1,
            key=f"stock_{item['id']}"
        )

        if item["stock"] < 20:
            st.warning("⚠️ Low stock item")

        if col3.button("Save", key=f"save_{item['id']}"):
            item["price"] = round(new_price, 2)
            item["stock"] = int(new_stock)
            save_inventory(inventory)
            st.success(f"{item['name']} updated successfully.")
            st.rerun()

        st.divider()


def page_admin_orders():
    st.header("📋 Customer Orders")

    orders = load_orders()

    if not orders:
        st.info("No customer orders have been placed yet.")
        return

    total_orders = len(orders)
    total_revenue = sum(order.get("total", 0) for order in orders)
    placed_orders = sum(1 for order in orders if order.get("status") == "Placed")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Orders", total_orders)
    col2.metric("Total Sales", f"${total_revenue:.2f}")
    col3.metric("Placed Orders", placed_orders)

    st.markdown("---")

    for order in reversed(orders):
        st.subheader(f"Order #{order.get('order_id')} - {order.get('customer')}")
        st.write(f"**Date:** {order.get('date')}")
        st.write(f"**Status:** {order.get('status')}")
        st.write(f"**Total:** ${order.get('total', 0):.2f}")

        for item in order.get("items", []):
            st.write(
                f"- {item['name']} | Qty: {item['quantity']} | "
                f"Price: ${item['price']:.2f} | Total: ${item['total']:.2f}"
            )

        st.divider()


def page_orders():
    inventory = load_inventory()

    st.header("🛍️ Shop Groceries")

    customer = st.session_state.user["username"]
    st.write(f"Ordering as: **{customer}**")

    sort_choice = st.selectbox(
        "Sort Products",
        ["Default", "Price: Low to High", "Price: High to Low"]
    )

    categories = sorted(
        set(item.get("category", "Other") for item in inventory if item["stock"] > 0)
    )

    if not categories:
        st.warning("No products currently in stock.")
        return

    category_labels = [
        f"{CATEGORY_ICONS.get(category, '🛒')} {category}"
        for category in categories
    ]

    tabs = st.tabs(category_labels)

    for tab, category in zip(tabs, categories):
        with tab:
            st.subheader(f"{CATEGORY_ICONS.get(category, '🛒')} {category}")

            category_items = [
                item for item in inventory
                if item["stock"] > 0 and item.get("category", "Other") == category
            ]

            if sort_choice == "Price: Low to High":
                category_items = sorted(category_items, key=lambda item: item["price"])
            elif sort_choice == "Price: High to Low":
                category_items = sorted(
                    category_items,
                    key=lambda item: item["price"],
                    reverse=True
                )

            columns = st.columns(3)

            for index, product in enumerate(category_items):
                with columns[index % 3]:
                    product_header_card(product["name"])

                    show_product_image(product.get("image"))

                    st.divider()

                    st.write(f"**Price:** ${product['price']:.2f}")
                    st.write(f"**Available Stock:** {product['stock']}")

                    if product["stock"] < 20:
                        st.warning("Low stock")

                    quantity = st.number_input(
                        "Quantity",
                        min_value=1,
                        max_value=int(product["stock"]),
                        step=1,
                        key=f"quantity_{product['id']}"
                    )

                    st.write(f"Item Total: **${quantity * product['price']:.2f}**")

                    col_add, col_fav = st.columns(2)

                    with col_add:
                        if st.button("Add to Cart", key=f"add_{product['id']}"):
                            cart, success, message = add_to_cart(
                                st.session_state.cart,
                                product,
                                quantity
                            )
                            st.session_state.cart = cart

                            if success:
                                st.success(message)
                            else:
                                st.error(message)

                    with col_fav:
                        is_favorited = any(
                            favorite["id"] == product["id"]
                            for favorite in st.session_state.favorites
                        )

                        if is_favorited:
                            if st.button(
                                "⭐ Favorited",
                                key=f"unfavorite_{product['id']}"
                            ):
                                st.session_state.favorites = remove_from_favorites(
                                    st.session_state.favorites,
                                    product["id"]
                                )
                                st.success(f"{product['name']} removed from favorites.")
                                st.rerun()
                        else:
                            if st.button(
                                "☆ Favorite",
                                key=f"favorite_{product['id']}"
                            ):
                                favorites, success, message = add_to_favorites(
                                    st.session_state.favorites,
                                    product
                                )
                                st.session_state.favorites = favorites

                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.info(message)


def page_favorites():
    st.header("⭐ Favorite Items")

    if not st.session_state.favorites:
        st.info("You have not added any favorite items yet.")
        return

    inventory = load_inventory()
    favorite_items = []

    for favorite in st.session_state.favorites:
        for item in inventory:
            if item["id"] == favorite["id"]:
                favorite_items.append(item)

    columns = st.columns(3)

    for index, product in enumerate(favorite_items):
        with columns[index % 3]:
            product_header_card(product["name"])

            show_product_image(product.get("image"))

            st.divider()

            st.write(f"**Category:** {product.get('category', 'Other')}")
            st.write(f"**Price:** ${product['price']:.2f}")
            st.write(f"**Available Stock:** {product['stock']}")

            if product["stock"] <= 0:
                st.warning("Out of stock")
            else:
                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    max_value=int(product["stock"]),
                    step=1,
                    key=f"fav_quantity_{product['id']}"
                )

                if st.button("Add to Cart", key=f"fav_add_{product['id']}"):
                    cart, success, message = add_to_cart(
                        st.session_state.cart,
                        product,
                        quantity
                    )
                    st.session_state.cart = cart

                    if success:
                        st.success(message)
                    else:
                        st.error(message)

            if st.button("Remove Favorite", key=f"remove_fav_{product['id']}"):
                st.session_state.favorites = remove_from_favorites(
                    st.session_state.favorites,
                    product["id"]
                )
                st.rerun()


def page_cart():
    st.header("🛒 Cart & Checkout")

    if not st.session_state.cart:
        st.info("Your cart is empty.")
        return

    st.subheader("Order Summary")

    cart_total = calculate_cart_total(st.session_state.cart)
    total_items = calculate_total_items(st.session_state.cart)

    col_a, col_b = st.columns(2)
    col_a.metric("Total Items", total_items)
    col_b.metric("Estimated Total", f"${cart_total:.2f}")

    st.markdown("---")

    for index, item in enumerate(st.session_state.cart):
        col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])

        col1.write(f"**{item['name']}**")
        col2.write(f"{CATEGORY_ICONS.get(item['category'], '🛒')} {item['category']}")
        col3.write(f"Qty: {item['quantity']}")
        col4.write(f"${item['total']:.2f}")

        if col5.button("Remove", key=f"remove_{index}"):
            st.session_state.cart.pop(index)
            st.rerun()

    st.markdown("---")

    st.subheader("Checkout")
    st.write(f"Subtotal: **${cart_total:.2f}**")
    st.write(f"Estimated Total: **${cart_total:.2f}**")

    col_place, col_clear = st.columns(2)

    with col_place:
        if st.button("Place Order"):
            inventory = load_inventory()
            enough_stock = True

            for cart_item in st.session_state.cart:
                for inventory_item in inventory:
                    if inventory_item["id"] == cart_item["id"]:
                        if cart_item["quantity"] > inventory_item["stock"]:
                            enough_stock = False
                            st.error(f"Not enough stock for {cart_item['name']}.")

            if enough_stock:
                for cart_item in st.session_state.cart:
                    for inventory_item in inventory:
                        if inventory_item["id"] == cart_item["id"]:
                            inventory_item["stock"] -= cart_item["quantity"]

                save_inventory(inventory)

                customer = st.session_state.user["username"]

                save_customer_order(
                    st.session_state.cart,
                    customer,
                    cart_total
                )

                st.session_state.cart = []

                st.balloons()

                st.success(
                    f"🎉 Thank you, {customer}! "
                    f"Your grocery order has been placed."
                )

    with col_clear:
        if st.button("Clear Cart"):
            st.session_state.cart = []
            st.rerun()


def page_ai_assistant():
    st.header("🤖 AI Grocery Assistant")

    inventory = load_inventory()

    user_question = st.text_input(
        "Ask the assistant:",
        placeholder="Example: What should I buy for breakfast?"
    )

    if st.button("Ask AI"):
        if user_question.strip() == "":
            st.error("Please enter a question.")
            return

        if "OPENAI_API_KEY" not in st.secrets:
            st.error("Missing OPENAI_API_KEY in Streamlit secrets.")
            return

        try:
            answer = get_ai_response(
                st.secrets["OPENAI_API_KEY"],
                inventory,
                user_question
            )

            st.success(answer)

        except Exception as e:
            st.error("The AI assistant could not respond.")
            st.write(e)


def page_profile(user):
    st.header("👤 User Profile")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Account Information")
        st.write(f"**Username:** {user['username']}")
        st.write(f"**Role:** {user['role']}")

        if user["role"] == "admin":
            st.success("Access Level: Full Inventory Management")
        else:
            st.info("Access Level: Grocery Ordering")

    with col2:
        st.subheader("Activity")

        cart_items = len(st.session_state.cart)
        cart_total = calculate_cart_total(st.session_state.cart)
        favorite_items = len(st.session_state.favorites)

        st.metric("Items in Cart", cart_items)
        st.metric("Favorite Items", favorite_items)
        st.metric("Current Cart Total", f"${cart_total:.2f}")

    st.markdown("---")

    st.subheader("Change Username")

    new_username = st.text_input("Enter New Username")

    if st.button("Update Username"):
        users = load_users()

        username_taken = any(
            existing_user["username"] == new_username
            for existing_user in users
        )

        if new_username.strip() == "":
            st.error("Username cannot be empty.")

        elif username_taken:
            st.error("Username already exists.")

        else:
            for existing_user in users:
                if existing_user["username"] == user["username"]:
                    existing_user["username"] = new_username

            save_users(users)
            st.session_state.user["username"] = new_username

            st.success("Username updated successfully.")
            st.rerun()

    st.markdown("---")

    st.subheader("System Information")
    st.write("**Application:** MISY350 Groceries")
    st.write("**Version:** 1.0 MVP")
    st.write("**System Status:** Active")

    st.markdown("---")

    if user["role"] == "user":
        col_clear_cart, col_clear_fav = st.columns(2)

        with col_clear_cart:
            if st.button("Clear Shopping Cart"):
                st.session_state.cart = []
                st.success("Shopping cart cleared.")
                st.rerun()

        with col_clear_fav:
            if st.button("Clear Favorites"):
                st.session_state.favorites = []
                st.success("Favorites cleared.")
                st.rerun()
    else:
        st.write("Admins can manage inventory and customer orders from the admin tabs.")


def logout_button():
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.cart = []
        st.session_state.favorites = []
        st.success("Logged out successfully.")
        st.rerun()


def login_register_page():
    st.markdown("""
        <div class="main-title">🛒 MISY350 Groceries</div>
        <div class="sub-title">Your campus grocery management system</div>
    """, unsafe_allow_html=True)

    st.info("""
    **Test Accounts**

    **User Account**  
    Username: `user@test.com`  
    Password: `user123`

    **Admin Account**  
    Username: `admin@test.com`  
    Password: `admin123`
    """)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

    with tab1:
        st.subheader("Welcome Back")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            success, user = login(username, password)

            if success:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success("Logged in successfully.")
                st.rerun()
            else:
                st.error("Invalid credentials.")

    with tab2:
        st.subheader("Create an Account")

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

    footer()


def logged_in_page():
    user = st.session_state.user

    welcome_header(user)
    sidebar_info(user)

    if user["role"] == "admin":
        inventory_tab, orders_tab, ai_tab, profile_tab, logout_tab = st.tabs(
            ["📦 Inventory", "📋 Orders", "🤖 AI Assistant", "👤 Profile", "🚪 Logout"]
        )

        with inventory_tab:
            page_inventory()

        with orders_tab:
            page_admin_orders()

        with ai_tab:
            page_ai_assistant()

        with profile_tab:
            page_profile(user)

        with logout_tab:
            st.header("🚪 Logout")
            st.write("Click below to log out of MISY350 Groceries.")
            logout_button()

    else:
        shop_tab, favorites_tab, cart_tab, ai_tab, profile_tab, logout_tab = st.tabs(
            ["🛍️ Shop", "⭐ Favorites", "🛒 Cart", "🤖 AI Assistant", "👤 Profile", "🚪 Logout"]
        )

        with shop_tab:
            page_orders()

        with favorites_tab:
            page_favorites()

        with cart_tab:
            page_cart()

        with ai_tab:
            page_ai_assistant()

        with profile_tab:
            page_profile(user)

        with logout_tab:
            st.header("🚪 Logout")
            st.write("Click below to log out of MISY350 Groceries.")
            logout_button()

    footer()


def run_app():
    st.set_page_config(page_title="MISY350 Groceries", layout="wide")

    initialize_session_state()
    add_style()

    if not st.session_state.logged_in:
        login_register_page()
    else:
        logged_in_page()
