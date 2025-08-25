import json
import csv
import io

products_json_str = """
[
  {"id": "prod001", "name": "Wireless Mouse"},
  {"id": "prod002", "name": "USB Keyboard"},
  {"id": "prod003", "name": "24-inch Monitor"},
  {"id": "prod004", "name": "Webcam HD"}
]
"""

inventory_csv_str = """ProductID,Quantity,Warehouse
prod001,55,Main
prod003,12,West Wing
prod002,78,Main
prod004,30,Annex
"""

products = json.loads(products_json_str)

inventory_by_id = {}
for row in csv.DictReader(io.StringIO(inventory_csv_str)):
    inventory_by_id[row["ProductID"]] = {
        "quantity": int(row["Quantity"]),
        "warehouse": row["Warehouse"]
    }

combined = []
for p in products:
    inv = inventory_by_id.get(p["id"], {"quantity": 0, "warehouse": None})
    combined.append({
        "id": p["id"],
        "name": p["name"],
        "quantity": inv["quantity"],
        "warehouse": inv["warehouse"],
    })

print(json.dumps(combined, ensure_ascii=False, indent=2))
