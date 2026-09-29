from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.api.deps import AdminUser, DBSession
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter()


@router.get("", response_model=list[CategoryRead])
def list_categories(db: DBSession) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.name)))


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: DBSession, _: AdminUser) -> Category:
    if payload.parent_id and db.get(Category, payload.parent_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent category not found")
    category = Category(name=payload.name.strip(), parent_id=payload.parent_id)
    db.add(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category name is already in use")
    db.refresh(category)
    return category


@router.patch("/{category_id}", response_model=CategoryRead)
def update_category(category_id: UUID, payload: CategoryUpdate, db: DBSession, _: AdminUser) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    if payload.parent_id == category_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="A category cannot be its own parent")
    if payload.parent_id and db.get(Category, payload.parent_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent category not found")
    if payload.name is not None:
        category.name = payload.name.strip()
    if "parent_id" in payload.model_fields_set:
        category.parent_id = payload.parent_id
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: UUID, db: DBSession, _: AdminUser) -> None:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    db.delete(category)
    db.commit()
