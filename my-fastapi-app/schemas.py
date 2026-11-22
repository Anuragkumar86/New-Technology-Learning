from typing import Annotated
from pydantic import BaseModel, Field, ConfigDict, computed_field

# 1. Shared fields used for both creating and returning a product
class ProductBase(BaseModel):
    name: Annotated[str, Field(..., min_length=2, max_length=100, description="Name of the Product", examples=["iPhone 16"])]
    category: Annotated[str, Field(..., max_length=50, description="Category of the Product", examples=["Electronics"])]
    price: Annotated[float, Field(..., gt=0, description="Price of the Product", examples=[799.99])]
    in_stock: Annotated[bool, Field(default=True, description="Checking if product is available in stock", examples=[True])]
    stock: Annotated[int, Field(default=0, ge=0, description="How much that product is available", examples=[12])]
    rating: Annotated[float, Field(default=0.0, ge=0, le=5, description="Rating of the Product", examples=[4.5])]
    tags: Annotated[list[str], Field(default=[], description="Tags of the Product", examples=[["wireless", "smartphone"]])]

# 2. Schema for POST /create (Notice: NO 'id' field here—PostgreSQL generates it!)
class ProductCreate(ProductBase):
    pass

# 3. Schema for API Responses (Includes database 'id' + your 'total_price' computed field!)
class ProductResponse(ProductBase):
    id: int

    # Allows Pydantic to convert SQLAlchemy ProductDB objects directly into JSON
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def total_price(self) -> float:
        return round(self.price * self.stock, 2)

class ProductUpdate(BaseModel):
    # Every field is optional (defaults to None), yet still validated if provided!
    name: Annotated[str | None, Field(default=None, min_length=2, max_length=100)]
    category: Annotated[str | None, Field(default=None, max_length=50)]
    price: Annotated[float | None, Field(default=None, gt=0)]
    in_stock: Annotated[bool | None, Field(default=None)]
    stock: Annotated[int | None, Field(default=None, ge=0)]
    rating: Annotated[float | None, Field(default=None, ge=0, le=5)]
    tags: Annotated[list[str] | None, Field(default=None)]