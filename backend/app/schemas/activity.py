from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.user import InteractionType
from app.schemas.product import ProductRead


class InteractionCreate(BaseModel):
    product_id: UUID
    interaction_type: InteractionType


class InteractionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    interaction_type: InteractionType
    created_at: datetime


class WishlistRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    created_at: datetime
    product: ProductRead
