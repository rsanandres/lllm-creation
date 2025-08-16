"""
Recommendation Engine Integration Example for AI Agent

This script demonstrates how an AI agent can:
- Implement basic recommendation logic
- Handle user preferences
- Process product specifications
- Generate personalized suggestions

All steps are thoroughly commented for learning purposes.
"""

from typing import List, Dict, Any, Optional
import random

# --- Example Product Data ---
# In a real system, this would come from a database or API
PRODUCTS = [
    {"id": 1, "name": "Server A", "category": "Compute", "cpu": 16, "ram": 64, "storage": 1000, "price": 1200.0},
    {"id": 2, "name": "Server B", "category": "Storage", "cpu": 8, "ram": 32, "storage": 4000, "price": 1500.0},
    {"id": 3, "name": "Server C", "category": "Compute", "cpu": 32, "ram": 128, "storage": 2000, "price": 2000.0},
    {"id": 4, "name": "Server D", "category": "Compute", "cpu": 8, "ram": 16, "storage": 500, "price": 800.0},
    {"id": 5, "name": "Server E", "category": "Storage", "cpu": 4, "ram": 16, "storage": 8000, "price": 2500.0},
]

# --- User Preferences Example ---
# In a real system, this would be user profile data or input
USER_PREFERENCES = {
    "preferred_category": "Compute",
    "min_cpu": 8,
    "min_ram": 32,
    "max_price": 2000.0
}

# --- Recommendation Logic ---
def recommend_products(
    products: List[Dict[str, Any]],
    user_prefs: Dict[str, Any],
    top_n: int = 3
) -> List[Dict[str, Any]]:
    """
    Recommend products based on user preferences and product specifications.
    Args:
        products: List of product dictionaries
        user_prefs: Dictionary of user preferences
        top_n: Number of recommendations to return
    Returns:
        List of recommended product dictionaries
    """
    # Filter products by user preferences
    filtered = []
    for product in products:
        # Check category preference
        if user_prefs.get("preferred_category") and product["category"] != user_prefs["preferred_category"]:
            continue
        # Check minimum CPU
        if product["cpu"] < user_prefs.get("min_cpu", 0):
            continue
        # Check minimum RAM
        if product["ram"] < user_prefs.get("min_ram", 0):
            continue
        # Check maximum price
        if product["price"] > user_prefs.get("max_price", float('inf')):
            continue
        filtered.append(product)

    # Sort by price ascending (cheapest first)
    filtered.sort(key=lambda x: x["price"])

    # If not enough matches, relax constraints (e.g., ignore category)
    if len(filtered) < top_n:
        # Try relaxing category constraint
        relaxed = [
            p for p in products
            if p["cpu"] >= user_prefs.get("min_cpu", 0)
            and p["ram"] >= user_prefs.get("min_ram", 0)
            and p["price"] <= user_prefs.get("max_price", float('inf'))
        ]
        # Add only new products not already in filtered
        for p in relaxed:
            if p not in filtered:
                filtered.append(p)
        # Sort again
        filtered.sort(key=lambda x: x["price"])

    # Return top N recommendations
    return filtered[:top_n]

# --- Personalized Suggestion Generation ---
def generate_suggestion_text(product: Dict[str, Any], user_prefs: Dict[str, Any]) -> str:
    """
    Generate a personalized suggestion message for a product.
    Args:
        product: Product dictionary
        user_prefs: User preferences dictionary
    Returns:
        Personalized suggestion string
    """
    return (
        f"We recommend '{product['name']}' with {product['cpu']} CPUs, {product['ram']}GB RAM, "
        f"and {product['storage']}GB storage for your needs. Price: ${product['price']:.2f}."
    )

# --- Example Usage ---
if __name__ == "__main__":
    # Step 1: Show user preferences
    print("User preferences:", USER_PREFERENCES)

    # Step 2: Get recommendations
    recommendations = recommend_products(PRODUCTS, USER_PREFERENCES, top_n=3)
    print("\nRecommended products:")
    for product in recommendations:
        print(product)

    # Step 3: Generate personalized suggestions
    print("\nPersonalized suggestions:")
    for product in recommendations:
        suggestion = generate_suggestion_text(product, USER_PREFERENCES)
        print(suggestion)

    # Step 4: Simulate a user with different preferences
    alt_prefs = {"preferred_category": "Storage", "min_cpu": 4, "min_ram": 8, "max_price": 3000.0}
    print("\nAlternative user preferences:", alt_prefs)
    alt_recommendations = recommend_products(PRODUCTS, alt_prefs, top_n=2)
    for product in alt_recommendations:
        print(generate_suggestion_text(product, alt_prefs)) 