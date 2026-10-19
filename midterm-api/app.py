
from flask import Flask, jsonify, request
from sqlalchemy.exc import IntegrityError
from models import db, Category, Item

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///inventory.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


# ---------- JSON Error Handlers ----------

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource or endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "HTTP method not allowed"}), 405


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"error": "Internal server error"}), 500


# ---------- Validation Helpers ----------

def read_json():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, (jsonify({"error": "A valid JSON object is required"}), 400)
    return data, None


def validate_category(data, updating=False):
    required = ["name", "description"]
    missing = [key for key in required if key not in data]
    if missing:
        return None, (jsonify({"error": "Missing required fields", "fields": missing}), 400)

    if not isinstance(data["name"], str) or not data["name"].strip():
        return None, (jsonify({"error": "name must be a non-empty string"}), 422)
    if not isinstance(data["description"], str) or not data["description"].strip():
        return None, (jsonify({"error": "description must be a non-empty string"}), 422)

    name = data["name"].strip()
    existing = Category.query.filter_by(name=name).first()
    if existing and (not updating or existing.id != updating):
        return None, (jsonify({"error": "Category name already exists"}), 409)

    return {"name": name, "description": data["description"].strip()}, None


def validate_item(data):
    required = ["name", "price", "stock", "category_id"]
    missing = [key for key in required if key not in data]
    if missing:
        return None, (jsonify({"error": "Missing required fields", "fields": missing}), 400)

    if not isinstance(data["name"], str) or not data["name"].strip():
        return None, (jsonify({"error": "name must be a non-empty string"}), 422)

    price = data["price"]
    stock = data["stock"]
    category_id = data["category_id"]
    status = data.get("status", "in_stock")

    if isinstance(price, bool) or not isinstance(price, (int, float)) or price < 0:
        return None, (jsonify({"error": "price must be a non-negative number"}), 422)
    if isinstance(stock, bool) or not isinstance(stock, int) or stock < 0:
        return None, (jsonify({"error": "stock must be a non-negative integer"}), 422)
    if isinstance(category_id, bool) or not isinstance(category_id, int) or category_id < 1:
        return None, (jsonify({"error": "category_id must be a positive integer"}), 422)
    if status not in ["in_stock", "out_of_stock"]:
        return None, (jsonify({"error": "status must be in_stock or out_of_stock"}), 422)

    if not Category.query.get(category_id):
        return None, (jsonify({"error": "category_id does not exist"}), 422)

    return {
        "name": data["name"].strip(),
        "price": float(price),
        "stock": stock,
        "status": status,
        "category_id": category_id
    }, None


# ---------- Parent Resource: Categories ----------

@app.route("/api/v1/categories", methods=["GET"])
def get_categories():
    categories = Category.query.order_by(Category.id).all()
    return jsonify({
        "count": len(categories),
        "data": [c.to_dict() for c in categories]
    }), 200


@app.route("/api/v1/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404
    return jsonify({"data": category.to_dict(include_items=True)}), 200


@app.route("/api/v1/categories", methods=["POST"])
def create_category():
    data, error = read_json()
    if error:
        return error
    values, error = validate_category(data)
    if error:
        return error

    category = Category(**values)
    db.session.add(category)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Category name already exists"}), 409
    return jsonify({"message": "Category created", "data": category.to_dict()}), 201


@app.route("/api/v1/categories/<int:category_id>", methods=["PUT"])
def update_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    data, error = read_json()
    if error:
        return error
    values, error = validate_category(data, updating=category.id)
    if error:
        return error

    category.name = values["name"]
    category.description = values["description"]
    db.session.commit()
    return jsonify({"message": "Category updated", "data": category.to_dict()}), 200


@app.route("/api/v1/categories/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": "Category and associated items deleted"}), 200


# ---------- Child Resource: Items ----------

@app.route("/api/v1/items", methods=["GET"])
def get_items():
    query = Item.query

    category_id = request.args.get("category_id")
    if category_id is not None:
        try:
            category_id = int(category_id)
        except ValueError:
            return jsonify({"error": "category_id must be an integer"}), 422
        query = query.filter_by(category_id=category_id)

    status = request.args.get("status")
    if status is not None:
        if status not in ["in_stock", "out_of_stock"]:
            return jsonify({"error": "Invalid status filter"}), 422
        query = query.filter_by(status=status)

    items = query.order_by(Item.id).all()
    return jsonify({"count": len(items), "data": [i.to_dict() for i in items]}), 200


@app.route("/api/v1/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    item = db.session.get(Item, item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    return jsonify({"data": item.to_dict()}), 200


@app.route("/api/v1/items", methods=["POST"])
def create_item():
    data, error = read_json()
    if error:
        return error
    values, error = validate_item(data)
    if error:
        return error

    item = Item(**values)
    db.session.add(item)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Item could not be created"}), 409
    return jsonify({"message": "Item created", "data": item.to_dict()}), 201


@app.route("/api/v1/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    item = db.session.get(Item, item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    data, error = read_json()
    if error:
        return error
    values, error = validate_item(data)
    if error:
        return error

    for key, value in values.items():
        setattr(item, key, value)

    db.session.commit()
    return jsonify({"message": "Item updated", "data": item.to_dict()}), 200


@app.route("/api/v1/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    item = db.session.get(Item, item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted"}), 200


# ---------- Start Server ----------

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
