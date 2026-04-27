import streamlit as st
import datetime
import json
import os   # ✅ NEW
from agent import process_ticket
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(page_title="AI Support Agent", layout="wide")

st.title("🤖 Autonomous Support Agent")
st.caption("Production-ready AI agent with tool-based reasoning")

# Load data
with open("data/tickets.json") as f:
    tickets = json.load(f)

if "results" not in st.session_state:
    st.session_state.results = None


# ===========================
# 🚀 RUN AGENT ON DATASET
# ===========================
if st.button("🚀 Run Agent on Tickets"):
    with st.spinner("Processing tickets..."):
        with ThreadPoolExecutor() as executor:
            st.session_state.results = list(executor.map(process_ticket, tickets))

    st.success("Processing complete!")

if st.session_state.results:
    results = st.session_state.results

    # Metrics
    resolved = sum(1 for r in results if r["result"] == "resolved")
    escalated = sum(1 for r in results if r["result"] == "escalated")
    failed = sum(1 for r in results if r["result"] == "failed")

    col1, col2, col3 = st.columns(3)
    col1.metric("✅ Resolved", resolved)
    col2.metric("⚠️ Escalated", escalated)
    col3.metric("❌ Failed", failed)

    # Table
    df = pd.DataFrame(results)
    df = df.drop_duplicates(subset=["ticket_id"])
    df = df.sort_values(by="confidence", ascending=False)

    st.subheader("📊 Ticket Summary")
    st.dataframe(df[["ticket_id", "result", "confidence", "category"]])

    # Select ticket
    ticket_ids = sorted({r["ticket_id"] for r in results})
    selected_ticket = st.selectbox(
        "Select Ticket to Inspect",
        ticket_ids,
        key="ticket_selector"
    )

    selected_data = [r for r in results if r["ticket_id"] == selected_ticket]
    if selected_data:
        selected_data = selected_data[0]
    else:
        st.error("No data found for selected ticket")
        st.stop()

    st.subheader(f"🔍 Ticket Details: {selected_ticket}")

    # Category
    st.write("### 📂 Category")
    st.info(selected_data.get("category", "N/A"))

    # Steps
    st.write("### 🧠 Steps Taken")
    for i, step in enumerate(selected_data["steps"], 1):
        st.write(f"{i}. {step}")

    # Result
    st.write("### 📌 Result")
    if selected_data["result"] == "resolved":
        st.success("Resolved")
    elif selected_data["result"] == "escalated":
        st.warning("⚠️ Escalated to human support")
    else:
        st.error("❌ Failed")

    if selected_data["result"] == "escalated":
        st.write("### 🧾 Escalation Summary")
        st.json(selected_data.get("escalation_summary", {}))

    if selected_data["result"] == "failed":
        st.write("### 💬 Reason")
        st.error(selected_data.get("reason", ""))
        st.write("### 📝 Explanation")
        st.info(selected_data.get("user_message", ""))

    # Confidence
    st.write(f"### 🎯 Confidence Score: {selected_data['confidence']}")
    st.progress(selected_data["confidence"])

    # Errors
    if selected_data["errors"]:
        st.error(selected_data["errors"])

    # ===========================
    # ✅ SAFE LOG SAVE (FIXED)
    # ===========================
    try:
        os.makedirs("logs", exist_ok=True)   # 🔥 IMPORTANT FIX

        with open("logs/audit_log.json", "w") as f:
            json.dump(results, f, indent=4)

    except Exception as e:
        st.warning(f"Logging failed: {e}")

    # Download button
    st.download_button(
        label="📥 Download Audit Log",
        data=json.dumps(results, indent=4),
        file_name="audit_log.json",
        mime="application/json"
    )


# ===========================
# 🧾 CREATE TICKET
# ===========================
st.subheader("🧾 Create Ticket")

col1, col2 = st.columns(2)

with col1:
    order_id = st.text_input("Order ID (e.g., ORD-1001)")
    issue_type = st.selectbox(
        "Issue Type",
        ["refund", "order_status", "general"]
    )

with col2:
    try:
        with open("data/customers.json", "r") as f:
            customers = json.load(f)
            valid_emails = [c["email"] for c in customers]
    except:
        valid_emails = []

    customer_email = st.text_input("Customer Email")

    if customer_email and customer_email not in valid_emails:
        st.warning("⚠️ Email not found in system. Using default test user.")
        customer_email = valid_emails[0] if valid_emails else customer_email


message = st.text_area("Describe the issue")

if st.button("Create & Process Ticket"):

    full_message = f"{issue_type} request for {order_id}. {message}"

    new_ticket = {
        "ticket_id": f"TKT-CUSTOM-{datetime.datetime.now().strftime('%H%M%S')}",
        "customer_email": customer_email,
        "subject": issue_type,
        "body": full_message,
        "source": "web",
        "created_at": datetime.datetime.now().isoformat(),
        "tier": 1
    }

    try:
        with open("data/tickets.json", "r") as f:
            existing = json.load(f)
    except:
        existing = []

    existing.append(new_ticket)

    with open("data/tickets.json", "w") as f:
        json.dump(existing, f, indent=4)

    result = process_ticket(new_ticket)

    st.subheader("🔍 Ticket Result")

    st.write("### 📂 Category")
    st.info(result.get("category", "N/A"))

    st.write("### 🧠 Steps Taken")
    for i, step in enumerate(result["steps"], 1):
        st.write(f"{i}. {step}")

    st.write("### 📌 Result")
    if result["result"] == "resolved":
        st.success("Resolved")
    elif result["result"] == "escalated":
        st.warning("Escalated")
    else:
        st.error("Failed")

    st.write(f"### 🎯 Confidence: {result['confidence']}")
    st.progress(result["confidence"])

    if result["errors"]:
        st.error(result["errors"])
