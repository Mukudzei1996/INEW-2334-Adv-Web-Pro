from flask import Flask, jsonify, request

app = Flask(__name__)

tasks = [
    {"id": 1, "title": "Configure NetLab VM", "priority": "high", "completed": True, "due_date": "2026-09-01"},
    {"id": 2, "title": "Implement Centralized Error Handlers", "priority": "medium", "completed": False, "due_date": "2026-09-15"},
    {"id": 3, "title": "Design SQLite Schema", "priority": "low", "completed": False, "due_date": "2026-09-22"}
]

ALLOWED_PRIORITIES = {"low", "medium", "high"}

# Custom Centralized Error Handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found", "status": 404}), 404

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"error": "Bad Request", "status": 400}), 400

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    priority_filter = request.args.get("priority")
    if priority_filter:
        filtered = [t for t in tasks if t["priority"].lower() == priority_filter.lower()]
        return jsonify({"count": len(filtered), "data": filtered}), 200
    return jsonify({"count": len(tasks), "data": tasks}), 200

@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": f"Task {task_id} not found", "status": 404}), 404
    return jsonify({"data": task}), 200

@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON request body", "status": 400}), 400
    
    # Required field check
    if "title" not in data or "priority" not in data:
        return jsonify({"error": "Missing required fields: 'title' and 'priority'", "status": 400}), 400
    
    # Value validation
    if not isinstance(data["title"], str) or not data["title"].strip():
        return jsonify({"error": "'title' must be a non-empty string", "status": 422}), 422
    if data["priority"].lower() not in ALLOWED_PRIORITIES:
        return jsonify({"error": f"'priority' must be one of {list(ALLOWED_PRIORITIES)}", "status": 422}), 422

    new_id = max([t["id"] for t in tasks], default=0) + 1
    new_task = {
        "id": new_id,
        "title": data["title"].strip(),
        "priority": data["priority"].lower(),
        "completed": bool(data.get("completed", False)),
        "due_date": data.get("due_date", "N/A")
    }
    tasks.append(new_task)
    return jsonify({"message": "Task created", "data": new_task}), 201

@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": f"Task {task_id} not found", "status": 404}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON request body", "status": 400}), 400
        
    if "title" in data:
        if not isinstance(data["title"], str) or not data["title"].strip():
            return jsonify({"error": "'title' cannot be empty", "status": 422}), 422
        task["title"] = data["title"].strip()
        
    if "priority" in data:
        if data["priority"].lower() not in ALLOWED_PRIORITIES:
            return jsonify({"error": f"'priority' must be one of {list(ALLOWED_PRIORITIES)}", "status": 422}), 422
        task["priority"] = data["priority"].lower()
        
    if "completed" in data:
        task["completed"] = bool(data["completed"])
        
    return jsonify({"message": "Task updated", "data": task}), 200

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    global tasks
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return jsonify({"error": f"Task {task_id} not found", "status": 404}), 404
    tasks = [t for t in tasks if t["id"] != task_id]
    return jsonify({"message": f"Task {task_id} deleted successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)