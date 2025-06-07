"""
Database Integration Example for AI Agent

This script demonstrates how an AI agent can:
- Connect to a product database (using SQLite for simplicity)
- Implement query handling
- Manage data persistence (CRUD operations)
- Handle concurrent operations (using threading)

All steps are thoroughly commented for learning purposes.
"""

import sqlite3  # SQLite is used for demonstration; in production, use PostgreSQL/MySQL/etc.
import threading  # For simulating concurrent operations
from typing import List, Dict, Any, Optional
import time

# --- Database Setup ---

def initialize_database(db_path: str = "products.db") -> None:
    """
    Create a simple products table if it doesn't exist.
    Args:
        db_path: Path to the SQLite database file
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    # Create table for products
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER
        )
    ''')
    conn.commit()
    conn.close()

# --- Database Connection Management ---

def get_connection(db_path: str = "products.db") -> sqlite3.Connection:
    """
    Get a new database connection.
    Args:
        db_path: Path to the SQLite database file
    Returns:
        sqlite3.Connection object
    """
    return sqlite3.connect(db_path)

# --- Data Persistence (CRUD Operations) ---

def add_product(product: Dict[str, Any], db_path: str = "products.db") -> int:
    """
    Add a new product to the database.
    Args:
        product: Dictionary with keys 'name', 'category', 'price', 'stock'
        db_path: Path to the database
    Returns:
        The ID of the inserted product
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)",
        (product['name'], product['category'], product['price'], product['stock'])
    )
    conn.commit()
    product_id = cursor.lastrowid
    conn.close()
    return product_id

def get_product_by_id(product_id: int, db_path: str = "products.db") -> Optional[Dict[str, Any]]:
    """
    Retrieve a product by its ID.
    Args:
        product_id: The product's ID
        db_path: Path to the database
    Returns:
        Product dictionary or None if not found
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "category": row[2], "price": row[3], "stock": row[4]}
    return None

def query_products(category: Optional[str] = None, db_path: str = "products.db") -> List[Dict[str, Any]]:
    """
    Query products, optionally filtering by category.
    Args:
        category: Category to filter by (optional)
        db_path: Path to the database
    Returns:
        List of product dictionaries
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    if category:
        cursor.execute("SELECT * FROM products WHERE category = ?", (category,))
    else:
        cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    conn.close()
    return [
        {"id": row[0], "name": row[1], "category": row[2], "price": row[3], "stock": row[4]}
        for row in rows
    ]

def update_product_stock(product_id: int, new_stock: int, db_path: str = "products.db") -> bool:
    """
    Update the stock of a product.
    Args:
        product_id: The product's ID
        new_stock: The new stock value
        db_path: Path to the database
    Returns:
        True if update was successful, False otherwise
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))
    conn.commit()
    updated = cursor.rowcount > 0
    conn.close()
    return updated

def delete_product(product_id: int, db_path: str = "products.db") -> bool:
    """
    Delete a product from the database.
    Args:
        product_id: The product's ID
        db_path: Path to the database
    Returns:
        True if deletion was successful, False otherwise
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    deleted = cursor.rowcount > 0
    conn.close()
    return deleted

# --- Concurrency Example: Simulate Multiple Agents Adding Products ---

def add_products_concurrently(products: List[Dict[str, Any]], db_path: str = "products.db") -> None:
    """
    Simulate concurrent addition of products using threads.
    Args:
        products: List of product dictionaries
        db_path: Path to the database
    """
    def worker(product):
        product_id = add_product(product, db_path)
        print(f"Added product with ID: {product_id}")
        time.sleep(0.1)  # Simulate some delay

    threads = []
    for product in products:
        t = threading.Thread(target=worker, args=(product,))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

# --- Example Usage ---
if __name__ == "__main__":
    # Step 1: Initialize the database (creates table if not exists)
    initialize_database()
    print("Database initialized.")

    # Step 2: Add some products concurrently
    sample_products = [
        {"name": "Server A", "category": "Compute", "price": 1200.0, "stock": 10},
        {"name": "Server B", "category": "Storage", "price": 1500.0, "stock": 5},
        {"name": "Server C", "category": "Compute", "price": 2000.0, "stock": 2},
    ]
    add_products_concurrently(sample_products)

    # Step 3: Query all products
    all_products = query_products()
    print("All products:", all_products)

    # Step 4: Update stock for a product
    if all_products:
        first_id = all_products[0]["id"]
        update_product_stock(first_id, 20)
        print(f"Updated stock for product ID {first_id}")

    # Step 5: Query by category
    compute_products = query_products(category="Compute")
    print("Compute products:", compute_products)

    # Step 6: Delete a product
    if all_products:
        last_id = all_products[-1]["id"]
        delete_product(last_id)
        print(f"Deleted product ID {last_id}")

    # Final: Show all products after deletion
    print("Products after deletion:", query_products()) 