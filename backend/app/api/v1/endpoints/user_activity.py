from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DBSession
from app.models.product import Product
from app.models.user import InteractionHistory, Wishlist
from app.schemas.activity import InteractionCreate, InteractionRead, WishlistRead

router = APIRouter()


def wishlist_query():
    return select(Wishlist).options(
        selectinload(Wishlist.product).selectinload(Product.images),
        selectinload(Wishlist.product).selectinload(Product.category),
    )


def get_wishlist_or_404(wishlist_id: UUID, db: DBSession) -> Wishlist:
    entry = db.scalar(wishlist_query().where(Wishlist.id == wishlist_id))
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist item not found")
    return entry


def ensure_product_exists(product_id: UUID, db: DBSession) -> None:
    if db.get(Product, product_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")


@router.get("/me/wishlist", response_model=list[WishlistRead])
def list_wishlist(db: DBSession, current_user: CurrentUser) -> list[Wishlist]:
    return list(
        db.scalars(
            wishlist_query().where(Wishlist.user_id == current_user.id).order_by(Wishlist.created_at.desc())
        )
    )


@router.post("/me/wishlist/{product_id}", response_model=WishlistRead, status_code=status.HTTP_201_CREATED)
def add_wishlist(product_id: UUID, db: DBSession, current_user: CurrentUser) -> Wishlist:
    ensure_product_exists(product_id, db)
    entry = db.scalar(select(Wishlist).where(Wishlist.user_id == current_user.id, Wishlist.product_id == product_id))
    if entry:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product is already in wishlist")
    entry = Wishlist(user_id=current_user.id, product_id=product_id)
    db.add(entry)
    db.commit()
    return get_wishlist_or_404(entry.id, db)


@router.delete("/me/wishlist/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_wishlist(product_id: UUID, db: DBSession, current_user: CurrentUser) -> None:
    entry = db.scalar(select(Wishlist).where(Wishlist.user_id == current_user.id, Wishlist.product_id == product_id))
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wishlist item not found")
    db.delete(entry)
    db.commit()


@router.get("/me/interactions", response_model=list[InteractionRead])
def list_interactions(db: DBSession, current_user: CurrentUser) -> list[InteractionHistory]:
    return list(
        db.scalars(
            select(InteractionHistory)
            .where(InteractionHistory.user_id == current_user.id)
            .order_by(InteractionHistory.created_at.desc())
        )
    )


@router.post("/me/interactions", response_model=InteractionRead, status_code=status.HTTP_201_CREATED)
def record_interaction(payload: InteractionCreate, db: DBSession, current_user: CurrentUser) -> InteractionHistory:
    ensure_product_exists(payload.product_id, db)
    interaction = InteractionHistory(
        user_id=current_user.id,
        product_id=payload.product_id,
        interaction_type=payload.interaction_type,
    )
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction
