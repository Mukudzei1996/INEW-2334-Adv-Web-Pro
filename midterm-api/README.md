# Midterm Project: Multi-Resource RESTful API

## Overview

This project is a RESTful API built with Python, Flask, Flask-SQLAlchemy, and SQLite. It manages product categories and items using a one-to-many relationship.

## Technologies

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- Thunder Client

## Setup and Running

1. Activate the virtual environment:

   ```bash
   source .venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Seed the database:

   ```bash
   python3 seed.py
   ```

4. Start the API:

   ```bash
   python3 app.py
   ```

The API runs at `http://127.0.0.1:5000`.

**Note:** Running `seed.py` resets the database and recreates the sample records.

## Database Models

- **Category:** Contains a unique name and description.
- **Item:** Contains a name, price, stock quantity, status, and category foreign key.

Each category can contain multiple items. Deleting a category also deletes its associated items.

## Category Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/categories` | List categories with item counts |
| GET | `/api/v1/categories/<id>` | Get one category and its items |
| POST | `/api/v1/categories` | Create a category |
| PUT | `/api/v1/categories/<id>` | Update a category |
| DELETE | `/api/v1/categories/<id>` | Delete a category and associated items |

### Example: Create a category

```json
{
  "name": "Electronics",
  "description": "Gadgets and hardware"
}
```

## Item Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/items` | List items |
| GET | `/api/v1/items/<id>` | Get one item |
| POST | `/api/v1/items` | Create an item |
| PUT | `/api/v1/items/<id>` | Update an item |
| DELETE | `/api/v1/items/<id>` | Delete an item |

The item listing endpoint supports filters such as:

- `/api/v1/items?category_id=1`
- `/api/v1/items?status=in_stock`

### Example: Create an item

```json
{
  "name": "Wireless Headphones",
  "price": 59.99,
  "stock": 20,
  "status": "in_stock",
  "category_id": 1
}
```

## HTTP Status Codes

- `200 OK`: Successful retrieval, update, or deletion.
- `201 Created`: Resource created successfully.
- `400 Bad Request`: Required fields are missing.
- `404 Not Found`: Resource does not exist.
- `409 Conflict`: Duplicate category name or other unique value.
- `422 Unprocessable Entity`: Invalid data, such as a negative price.

Errors are returned as JSON responses.

## Database Seeding

Run `python3 seed.py` to create the SQLite tables and populate the database with at least three categories and six items.

## Testing

The Thunder Client collection is provided in `thunder-collection_midterm.json`. It contains requests for CRUD operations, filtering, validation, and error responses.
