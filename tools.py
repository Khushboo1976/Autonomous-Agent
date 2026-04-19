import json
import random

# Load data
with open("data/orders.json") as f:
    orders = json.load(f)

with open("data/customers.json") as f:
    customers = json.load(f)

with open("data/products.json") as f:
    products = json.load(f)


def get_order(order_id):
    for order in orders:
        if str(order["order_id"]) == str(order_id):
            return order
    raise Exception("Order not found")


def get_customer(email):
    for customer in customers:
        if customer["email"] == email:
            return customer
    raise Exception("Customer not found")


def get_product(product_id):
    for product in products:
        if str(product["product_id"]) == str(product_id):
            return product
    raise Exception("Product not found")


def check_refund_eligibility(order_id):
    order = get_order(order_id)
    if order["status"] == "delivered":
        return {"eligible": True, "reason": "Delivered item"}
    return {"eligible": False, "reason": "Not delivered yet"}


def issue_refund(order_id, amount):
    return f"Refund issued for {order_id} of amount {amount}"


def send_reply(ticket_id, message):
    return f"Reply sent to {ticket_id}"


def escalate(ticket_id, summary, priority):
    return f"Escalated {ticket_id} with priority {priority}"


def search_knowledge_base(query):
    with open("data/knowledge-base.md", "r") as f:
        kb = f.read()

    if any(word in kb.lower() for word in query.lower().split()):
        return "Relevant policy found: Please follow refund guidelines."
    
    return "No relevant info found"