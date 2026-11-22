from fastapi import FastAPI, HTTPException, Query
import json
app = FastAPI()
from schema.product import Product
from fastapi.responses import JSONResponse
def fetchData():
    with open("data.json", "r") as file:
        data = json.load(file)

    return data


@app.get("/")
def home():
    return {"message: ": "Welcom Anurag to Home Page..."}


@app.get("/all-product")
def getAll():
    all = fetchData()

    return {"All records: ": all}


@app.get("/all-product/{id}")
def getAll(id: int):
    all = fetchData()

    for product in all:
        if product["id"] == id:
            return product
    
    raise HTTPException(status_code=404, detail=f"User not found with this id {id}")


@app.get("/sort")
def sort_record(
    sort_by: str = Query(default="price", description=f"Sort the result by sort_by type"), 
    order: str = Query(default="asc", description="Sort in ascending or decending")):

    valid_fields = ["price", "stock", "rating"]

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=" The chosen sort_by value is not valid")


    is_decending = order == "desc"

    all_records = fetchData()

    sorted_records = sorted(all_records, key= lambda records: records[sort_by], reverse=is_decending)

    return sorted_records

#---------------------------------------------------------------------

@app.post("/create")
def add_product(product: Product):

    existing_products = fetchData()
    new_pr = product.model_dump()
    existing_products.append(new_pr)
    with open("data.json", "w") as f:

        json.dump(existing_products, f, indent=4)

    return JSONResponse(content="Product added Successfully...✅✅", status_code=201)