import asyncio
import json
import os
import secrets
import time
from contextlib import asynccontextmanager
from typing import Annotated

from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Request, Security
from fastapi.responses import StreamingResponse
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, SessionLocal, engine
from models import ProductDB
from schemas import ProductCreate, ProductResponse, ProductUpdate

load_dotenv()

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")
if not ADMIN_API_KEY:
    raise RuntimeError("ADMIN_API_KEY is missing from environment!")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when FastAPI boots up: creates 'products' table if it doesn't exist yet!
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Shop API with PostgreSQL", lifespan=lifespan)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


dbSession = Annotated[Session, Depends(get_db)]


async def send_email(product_id: int, product_name: str, price: float):

    time.sleep(10)
    print(
        f"[BACKGROUND-TASK-SENDING-EMAIL] to product with id: {product_id}, Name: {product_name}, Price: {price}...✅🎉✅"
    )


# ---------------------------LIVE STREAMING --------------------------------------
async def product_stream_live(request: Request):
    try:
        # 1. Fetch all products ONCE at the start of the stream (or fetch just their IDs)
        with SessionLocal() as db:
            all_products = db.execute(select(ProductDB)).scalars().all()
            # Convert to plain dicts right away before 'with SessionLocal()' closes the DB session!
            products_data = [
                {"id": p.id, "name": p.name, "category": p.category, "stock": p.stock}
                for p in all_products
            ]

        # 2. Loop through ONE product at a time instead of sending the whole list!
        for item in products_data:
            if await request.is_disconnected():
                break

            # 3. Yield ONLY this single product dict, then pause 2 seconds before the next one
            yield f"data: {json.dumps(item)}\n\n"
            await asyncio.sleep(2)

        # Optional: Tell the browser the stream finished sending all items
        yield f"data: {json.dumps({'status': 'completed'})}\n\n"

    except asyncio.CancelledError:
        print("STREAM CANCELLED BY SERVER SHUTDOWN 🛑")
    finally:
        print("CLIENT DISCONNECTED OR STREAM ENDED ❌")


# -----------------------------SECURITY-------------------------------------------------

ADMIN_API_KEY = "anurag-secret-123"

header_extractor = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_admin_api_key(
    incoming_key: Annotated[str | None, Security(header_extractor)],
):
    if incoming_key is None:
        raise HTTPException(status_code=401, detail="X-API-KEY is missing in Header")

    if not secrets.compare_digest(incoming_key, ADMIN_API_KEY):
        raise HTTPException(status_code=401, detail="Wrong API Key!")

    # Step C: Key is valid! Let the user enter the route.
    return incoming_key


AdminAuth = Annotated[str | None, Depends(verify_admin_api_key)]


# -------------------------------ROUTES----------------------------------------------
@app.post("/create", response_model=ProductResponse, status_code=201)
def create_product(
    product: ProductCreate,
    db: dbSession,
    bg_tasks: BackgroundTasks,
    admin_api: AdminAuth,
):

    new_product = ProductDB(**product.model_dump())

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    bg_tasks.add_task(send_email, new_product.id, new_product.name, new_product.price)
    return new_product


@app.get("/products", response_model=list[ProductResponse])
def get_all_products(db: dbSession):

    products = db.execute(select(ProductDB)).scalars().all()
    return products


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: dbSession):
    product = db.get(ProductDB, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@app.delete(
    "/products/{product_id}",
    status_code=204,
    dependencies=[Depends(verify_admin_api_key)],
)
def delete_product(product_id: int, db: dbSession):
    product = db.get(ProductDB, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()
    return None


@app.patch("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_update: ProductUpdate, db: dbSession):
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


# -----------------------------LIVE STREAMING------------------------------------
@app.get("/live/products")
def get_live_products(request: Request):

    return StreamingResponse(
        product_stream_live(request), media_type="text/event-stream"
    )
