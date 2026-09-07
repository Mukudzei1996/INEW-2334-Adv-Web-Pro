from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory mock database
items = [
    {"id": 1, "name": "Web Architecture", "category": "Core", "active": True},
    {"id": 2, "name": "Database Systems", "category": "Data", "active": True},
    {"id": 3, "name": "API Security", "category": "Security", "active": False}
]

@app.route("/api/status", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "service": "catalog-api", "version": "1.0.0"}), 200

@app.route("/api/items", methods=["GET"])
def get_items():
    return jsonify({"count": len(items), "data": items}), 200

@app.route("/api/items/<int:item_id>", methods=["GET"])
def get_item_by_id(item_id):
    item = next((i for i in items if i["id"] == item_id), None)
    if not item:
        return jsonify({"error": f"Item with ID {item_id} not found"}), 404
    return jsonify({"data": item}), 200

@app.route("/api/items", methods=["POST"])
def create_item():
    data = request.get_json()
    if not data or "name" not in data or "category" not in data:
        return jsonify({"error": "Invalid payload. 'name' and 'category' are required."}), 400
    
    new_id = max([i["id"] for i in items], default=0) + 1
    new_item = {
        "id": new_id,
        "name": data["name"],
        "category": data["category"],
        "active": data.get("active", True)
    }
    items.append(new_item)
    return jsonify({"message": "Item created successfully", "data": new_item}), 201

if __name__ == "__main__":
    app.run(debug=True, port=5000)