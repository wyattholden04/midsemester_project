import streamlit as st
import json
from pathlib import Path

jsonfile = Path("inventory.json")

def load_inventory():
    if not jsonfile.exists():
        return []

    try:
        data = json.loads(jsonfile.read_text())
        if not isinstance(data, list):
            raise ValueError("inventory data is not a list")
        return data
    except Exception:
        return []


def save_inventory(data):
    jsonfile.write_text(json.dumps(data, indent=4))


def app():
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


if __name__ == "__main__":
    app()