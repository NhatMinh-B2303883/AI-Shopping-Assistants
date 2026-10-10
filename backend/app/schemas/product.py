from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.category import CategoryRead


class ProductImageCreate(BaseModel):
    image_url: str = Field(min_length=1, max_length=2048)
    is_primary: bool = False


class ProductImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    image_url: str
    is_primary: bool


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    category_id: UUID | None = None
    gender: str | None = Field(default=None, max_length=30)
    color: str | None = Field(default=None, max_length=50)
    price: Decimal | None = None
    external_id: str | None = Field(default=None, max_length=64)
    canonical_text: str | None = None
    images: list[ProductImageCreate] = Field(default_factory=list)


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    category_id: UUID | None = None
    gender: str | None = Field(default=None, max_length=30)
    color: str | None = Field(default=None, max_length=50)
    price: Decimal | None = None
    external_id: str | None = Field(default=None, max_length=64)
    canonical_text: str | None = None
    images: list[ProductImageCreate] | None = None


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    category_id: UUID | None
    category: CategoryRead | None = None
    gender: str | None
    color: str | None
    price: Decimal | None
    external_id: str | None = None
    canonical_text: str | None = None
    created_at: datetime
    updated_at: datetime
    images: list[ProductImageRead]


class ProductListResponse(BaseModel):
    items: list[ProductRead]
    total: int
    limit: int
    offset: int


class PriceRange(BaseModel):
    min: Decimal | None
    max: Decimal | None


class FilterFacetsResponse(BaseModel):
    colors: list[str]
    genders: list[str]
    price: PriceRange
