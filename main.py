from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 550, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 80, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Spoon", "price": 100, "category": "Kitchen", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 50, "category": "Stationery", "in_stock": True},
    {"id": 5, "name": "Laptop Stand", "price": 1500, "category": "Accessories", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 3500, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 2500, "category": "Electronics", "in_stock": False},
]

@app.get("/products")
def get_products():
    return {
        "products": products,
        "total": len(products)
    }

@app.get("/products/category/{category_name}")
def get_products_by_category(category_name: str):
    filtered = [p for p in products if p["category"].lower() == category_name.lower()]
    if not filtered:
        return {"error": "No products found in this category"}
    return {
        "products": filtered,
        "total": len(filtered)
    }

@app.get("/products/instock")
def get_instock_products():
    instock = [p for p in products if p["in_stock"]]
    return {
        "in_stock_products": instock,
        "count": len(instock)
    }

@app.get("/store/summary")
def store_summary():
    total_products = len(products)
    count_in_stock = sum(1 for item in products if item["in_stock"])
    count_out_of_stock = sum(1 for item in products if not item["in_stock"])
    categories = list({item["category"] for item in products})
    return {
        "store_name": "My E-commerce Store",
        "total_products": total_products,
        "in_stock": count_in_stock,
        "out_of_stock": count_out_of_stock,
        "categories": categories
    }

@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    lower_keyword = keyword.lower()
    matched = [p for p in products if lower_keyword in p["name"].lower()]
    if not matched:
        return {"message": "No products matched your search"}
    return {
        "matched_products": matched,
        "count": len(matched)
    }

@app.get("/products/deals")
def product_deals():
    best_deal = min(products, key=lambda p: p["price"])
    premium_pick = max(products, key=lambda p: p["price"])
    return {
        "best_deal": best_deal,
        "premium_pick": premium_pick
    }

@app.get("/products/filter")
def filter_products(
    category: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None)
):
    filtered = products

    if category:
        filtered = [p for p in filtered if p["category"].lower() == category.lower()]

    if min_price is not None:
        filtered = [p for p in filtered if p["price"] >= min_price]

    if max_price is not None:
        filtered = [p for p in filtered if p["price"] <= max_price]

    if not filtered:
        return {"message": "No products matched your filters"}
    return {
        "filtered_products": filtered,
        "count": len(filtered)
    }
    
@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        return {"error": "Product not found"}
    return {
        "name": product["name"],
        "price": product["price"]
    }   

# Feedback storage
feedback = []

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())
    return {
        "message": "Feedback submitted successfully",
        "feedback": data.dict(),
        "total_feedback": len(feedback)
    }
    
@app.get("/products/summary")
def product_summary():
    total_products = len(products)
    in_stock_count = sum(1 for p in products if p["in_stock"])
    out_of_stock_count = sum(1 for p in products if not p["in_stock"])
    cheapest = min(products, key=lambda p: p["price"])
    most_expensive = max(products, key=lambda p: p["price"])

    categories = list({p["category"] for p in products})

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_count": out_of_stock_count,
        "most_expensive": {"name": most_expensive["name"], "price": most_expensive["price"]},
        "cheapest": {"name": cheapest["name"], "price": cheapest["price"]},
        "categories": categories
    }

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)
class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)   
    items: List[OrderItem] = Field(..., min_items=1)

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
            continue

        if not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
            continue

        subtotal = product["price"] * item.quantity
        confirmed.append({"product": product["name"], "qty": item.quantity, "subtotal": subtotal})
        grand_total += subtotal

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

class SimpleOrder(BaseModel):
    order_id: int
    company_name: str
    contact_email: str
    items: List[dict]
    status: str

class OrderRequest(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[dict] = Field(..., min_items=1)

orders = []
order_counter = 0

@app.post("/orders")
def place_order(order: OrderRequest):
    global order_counter
    order_counter += 1
    new_order = {
        "order_id": order_counter,
        "company_name": order.company_name,
        "contact_email": order.contact_email,
        "items": order.items,
        "status": "pending"
    }
    orders.append(new_order)
    return {"message": "Order placed successfully", "order": new_order}

@app.get("/orders/{order_id}")
def get_order(order_id: int):
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if not order:
        return {"error": "Order not found"}
    return order

@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    order = next((o for o in orders if o["order_id"] == order_id), None)
    if not order:
        return {"error": "Order not found"}
    order["status"] = "confirmed"
    return {"message": "Order confirmed successfully", "order": order}

class Product(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool
@app.post("/products")
def add_product(product: Product):
    # if product name already exists
    for p in products:
        if p["name"].lower() == product.name.lower():
            return {"error": "Product with this name already exists"}, 400
    new_id = max(p["id"] for p in products) + 1 if products else 1
    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }
    products.append(new_product)
    return {"message": "Product added", "product": new_product}

@app.put("/products/{product_id}")
def update_product(product_id: int,
                   price: Optional[int] = None,
                   in_stock: Optional[bool] = None):
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return {"error": "Product not found"}, 404
    if price is not None:
        product["price"] = price
    if in_stock is not None:
        product["in_stock"] = in_stock

    return {"message": "Product updated", "product": product}

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return {"error": "Product not found"}, 404
    products.remove(product)
    return {"message": f"Product '{product['name']}' deleted"}

@app.get("/products/audit")
def audit_products():
    total_products = len(products)
    in_stock_count = sum(1 for p in products if p["in_stock"])
    out_of_stock_names = [p["name"] for p in products if not p["in_stock"]]

    total_stock_value = sum(p["price"] * 10 for p in products if p["in_stock"])

    most_expensive = max(products, key=lambda p: p["price"])

    return {
        "total_products": total_products,
        "in_stock_count": in_stock_count,
        "out_of_stock_names": out_of_stock_names,
        "total_stock_value": total_stock_value,
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        }
    }

@app.put("/products/discount")
def apply_discount(category: str, discount_percent: int):
    if discount_percent < 1 or discount_percent > 99:
        return {"error": "Discount percent must be between 1 and 99"}, 400

    updated = []
    for p in products:
        if p["category"].lower() == category.lower():
            new_price = int(p["price"] * (1 - discount_percent / 100))
            p["price"] = new_price
            updated.append({"id": p["id"], "name": p["name"], "new_price": new_price})
    if not updated:
        return {"message": f"No products found in category '{category}'"}

    return {
        "message": f"Applied {discount_percent}% discount to {len(updated)} products in {category}",
        "updated_products": updated
    }
