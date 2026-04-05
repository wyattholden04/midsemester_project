import streamlit as st
import pandas as pd

st.set_page_config(page_title="Orders", layout="wide")

inventory = [
    {"id": 1, "name": "Eggs (1 Dozen)", "price": 2.25, "stock": 23},
    {"id": 2, "name": "Milk (1 Gallon)", "price": 2.99, "stock": 21},
    {"id": 3, "name": "Ground Beef (1 lb)", "price": 7.49, "stock": 20},
    {"id": 4, "name": "Chicken Breast (5 Pack)", "price": 12.99, "stock": 18},
    {"id": 5, "name": "Orange Juice (46 fl oz)", "price": 6.49, "stock": 19}
]

if "orders" not in st.session_state:
    st.session_state.orders = [
        {"order_id": 1, "customer": "Matt", "item": "Eggs (1 Dozen)", "quantity": 2, "total": 4.50, "status": "Placed"},
        {"order_id": 2, "customer": "Sarah", "item": "Milk (1 Gallon)", "quantity": 1, "total": 2.99, "status": "Completed"},
        {"order_id": 3, "customer": "Jake", "item": "Ground Beef (1 lb)", "quantity": 3, "total": 22.47, "status": "Placed"}
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