
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)

    items = db.relationship(
        "Item",
        backref="category",
        cascade="all, delete-orphan",
        lazy=True
    )

    def to_dict(self, include_items=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "item_count": len(self.items)
        }

        if include_items:
            data["items"] = [item.to_dict() for item in self.items]

        return data


class Item(db.Model):
    __tablename__ = "items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default="in_stock")
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "stock": self.stock,
            "status": self.status,
            "category_id": self.category_id
        }
