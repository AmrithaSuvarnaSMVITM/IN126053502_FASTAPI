from fastapi import FastAPI
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
    matched = [p for p in products if lower_keyword in p["name"].lower()]# convert to lowercase for easy search

    if not matched:
        return {"message": "No products matched your search"}

    return {
        "matched_products": matched,
        "count": len(matched)
    }
@app.get("/products/deals")
def product_deals():
    # lambda helps to compare items
    best_deal = min(products, key=lambda p: p["price"])
    premium_pick = max(products, key=lambda p: p["price"])

    return {
        "best_deal": best_deal,
        "premium_pick": premium_pick
    }