import json
import os   # ✅ NEW (for folder handling)
from agent import process_ticket
from concurrent.futures import ThreadPoolExecutor

# ===========================
# 📥 LOAD DATA
# ===========================
with open("data/tickets.json") as f:
    tickets = json.load(f)

audit_logs = []
failed_tickets = []

def run(ticket):
    return process_ticket(ticket)

# ===========================
# 🚀 PROCESS TICKETS
# ===========================
with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(run, tickets)

for r in results:
    audit_logs.append(r)

    if r["result"] == "failed":
        failed_tickets.append(r)

# ===========================
# 📁 SAFE LOGGING (FIXED)
# ===========================
try:
    os.makedirs("logs", exist_ok=True)   # 🔥 IMPORTANT FIX

    # Save main audit log
    with open("logs/audit_log.json", "w") as f:
        json.dump(audit_logs, f, indent=4)

    # Save failed tickets separately
    with open("logs/failed_tickets.json", "w") as f:
        json.dump(failed_tickets, f, indent=4)

except Exception as e:
    print(f"[LOGGING ERROR] {e}")

print("Done ✅")
