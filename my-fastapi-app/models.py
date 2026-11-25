from sqlalchemy import Boolean, Float, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class ProductDB(Base):
    # 1. Exact table name inside PostgreSQL
    __tablename__ = "products"

    # 2. Auto-incrementing Primary Key (PostgreSQL generates 1, 2, 3... automatically)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # 3. Core columns matching your data.json fields
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    stock: Mapped[int] = mapped_column(Integer, default=0)
    rating: Mapped[float] = mapped_column(Float, default=0.0)

    # 4. PostgreSQL native array of strings for tags
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
