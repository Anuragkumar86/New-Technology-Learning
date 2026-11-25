from typing import Annotated

from pydantic import BaseModel, Field, computed_field


class Product(BaseModel):
    id: Annotated[str, Field(..., description="Id of the Product", examples=["13"])]
    name: Annotated[
        str, Field(..., description="Name of the Product", examples=["iphone"])
    ]
    category: Annotated[
        str, Field(..., description="Category of the Product", examples=["Electronics"])
    ]
    price: Annotated[
        float, Field(..., description="Price of the Product", examples=[34.5])
    ]
    in_stock: Annotated[
        bool,
        Field(
            ...,
            description="Checking if product is available in stock",
            examples=[True],
        ),
    ]
    stock: Annotated[
        int, Field(..., description="How much that product is available", examples=[12])
    ]
    rating: Annotated[
        float,
        Field(..., description="Rating of the Product", ge=0, lt=5, examples=[3.5]),
    ]
    tags: Annotated[
        list[str],
        Field(
            ...,
            description="Tags of the Product",
            examples=[["wireless", "mechanical", "rgb"]],
        ),
    ]

    @computed_field
    @property
    def total_price(self) -> float:
        return round(self.price * self.stock, 2)
