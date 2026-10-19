
from app import app
from models import db, Category, Item

with app.app_context():
    # Clear existing data and recreate tables
    db.drop_all()
    db.create_all()

    # Create 3 parent records
    electronics = Category(
        name="Electronics",
        description="Gadgets and computer hardware"
    )
    office = Category(
        name="Office Supplies",
        description="Stationery and desk equipment"
    )
    furniture = Category(
        name="Furniture",
        description="Office and home furniture"
    )

    db.session.add_all([electronics, office, furniture])
    db.session.commit()

    # Create 6 child records: 2 items per category
    items = [
        Item(
            name="Mechanical Keyboard",
            price=89.99,
            stock=15,
            status="in_stock",
            category_id=electronics.id
        ),
        Item(
            name="USB-C Hub",
            price=29.99,
            stock=40,
            status="in_stock",
            category_id=electronics.id
        ),
        Item(
            name="Notebook Pack",
            price=8.50,
            stock=25,
            status="in_stock",
            category_id=office.id
        ),
        Item(
            name="Desk Organizer",
            price=14.50,
            stock=0,
            status="out_of_stock",
            category_id=office.id
        ),
        Item(
            name="Office Desk",
            price=179.99,
            stock=5,
            status="in_stock",
            category_id=furniture.id
        ),
        Item(
            name="Ergonomic Chair",
            price=129.99,
            stock=8,
            status="in_stock",
            category_id=furniture.id
        )
    ]

    db.session.add_all(items)
    db.session.commit()

    print("Database seeded successfully!")
    print(f"Categories created: {Category.query.count()}")
    print(f"Items created: {Item.query.count()}")
