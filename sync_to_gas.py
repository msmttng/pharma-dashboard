import json
import os
import sys

# GAS_WEBAPP_URL is expected to be in .env or passed as environment variable
# If not available, we skip sync but don't crash
def main():
    json_path = os.path.join(os.path.dirname(__file__), "pharma_data.json")
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return

    pending_items = []
    
    # Collect from Collabo (checks status and remarks)
    for item in data.get("collabo", []):
        name = item.get("name", "").strip()
        status = item.get("status", "")
        remarks = item.get("remarks", "")
        if any(s in status or s in remarks for s in ["未納", "未定", "調達中"]):
            if name and name not in pending_items:
                pending_items.append(name)

    # Collect from Medipal
    for item in data.get("medipal", []):
        name = item.get("name", "").strip()
        remarks = item.get("remarks", "")
        if any(s in remarks for s in ["未納", "未定", "調整"]):
            if name and name not in pending_items:
                pending_items.append(name)

    # Collect from Alfweb
    for item in data.get("alfweb", []):
        name = item.get("name", "").strip()
        status = item.get("status", "")
        if any(s in status for s in ["未納", "未定", "停止", "未定"]):
            if name and name not in pending_items:
                pending_items.append(name)

    print(f"Found {len(pending_items)} pending items.")

    # Get GAS URL from environment (provided by run_dashboard.bat or .env)
    gas_url = os.environ.get("GAS_WEBAPP_URL")
    if not gas_url:
        print("Skipping sync: GAS_WEBAPP_URL not set in environment.")
        return

    # Use urllib instead of requests to avoid dependency issues if possible, 
    # but we'll try to use a simple approach.
    import urllib.request
    import urllib.parse

    payload = {
        "action": "sync_dashboard",
        "items": pending_items
    }
    
    try:
        req = urllib.request.Request(
            gas_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req) as res:
            print(f"Sync success: {res.read().decode('utf-8')}")
    except Exception as e:
        print(f"Sync failed: {e}")

if __name__ == "__main__":
    main()
