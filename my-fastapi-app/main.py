from database import SessionLocal
from fastapi import FastAPI, Depends, HTTPException
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy import select
from models import ProductDB
from schemas import ProductCreate, ProductResponse, ProductUpdate

app = FastAPI(title="Shop API with PostgreSQL")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

dbSession = Annotated[Session, Depends(get_db)]

@app.post("/create", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db:dbSession):

   new_product = ProductDB(**product.model_dump())

   db.add(new_product)
   db.commit()
   db.refresh(new_product)

   return new_product

@app.get("/products", response_model=list[ProductResponse])
def get_all_products(db : dbSession):

    products = db.execute(select(ProductDB)).scalars().all()
    return products


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db:dbSession):
    product = db.get(ProductDB, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db:dbSession):
    product = db.get(ProductDB, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return None


@app.patch("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_update: ProductUpdate, db:dbSession):
    product = db.get(ProductDB, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = product_update.model_dump(exclude_unset=True)

    # Update those attributes on the SQLAlchemy object
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return product

