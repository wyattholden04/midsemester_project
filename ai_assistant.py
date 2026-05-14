from openai import OpenAI


def build_inventory_text(inventory):
    inventory_text = ""

    for item in inventory:
        inventory_text += (
            f"- {item['name']} | Category: {item.get('category', 'Other')} | "
            f"Price: ${item['price']} | Stock: {item['stock']}\n"
        )

    return inventory_text


def get_ai_response(api_key, inventory, user_question):
    client = OpenAI(api_key=api_key)

    inventory_text = build_inventory_text(inventory)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"""
You are the AI Grocery Assistant for MISY350 Groceries.

Use only the inventory below when making recommendations.

Current inventory:
{inventory_text}

User question:
{user_question}

Give a helpful answer in 3-6 sentences. Mention item names, prices, and stock when useful.
"""
    )

    return response.output_text
