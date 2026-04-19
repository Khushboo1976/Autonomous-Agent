import json
from agent import process_ticket
from concurrent.futures import ThreadPoolExecutor

with open("data/tickets.json") as f:
    tickets = json.load(f)

audit_logs = []
failed_tickets = []

def run(ticket):
    return process_ticket(ticket)

with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(run, tickets)

for r in results:
    audit_logs.append(r)

    if r["result"] == "failed":
        failed_tickets.append(r)

# SAVE LOGS
with open("logs/audit_log.json", "w") as f:
    json.dump(audit_logs, f, indent=4)

# 🔥 DEAD LETTER FILE
with open("logs/failed_tickets.json", "w") as f:
    json.dump(failed_tickets, f, indent=4)

print("Done ✅")