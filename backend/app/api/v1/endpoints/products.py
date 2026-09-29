from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.api.deps import AdminUser, DBSession
from app.models.category import Category
from app.models.product import Product, ProductImage
from app.schemas.product import (
    FilterFacetsResponse,
    PriceRange,
    ProductCreate,
    ProductListResponse,
    ProductRead,
    ProductUpdate,
)

router = APIRouter()


def product_query():
    return select(Product).options(selectinload(Product.images), selectinload(Product.category))


def descendant_category_ids(category_id: UUID):
    """Return a recursive CTE containing the chosen category and all descendants."""
    category_tree = select(Category.id).where(Category.id == category_id).cte(name="category_tree", recursive=True)
    child_categories = Category.__table__.alias("child_categories")
    return category_tree.union_all(
        select(child_categories.c.id).where(child_categories.c.parent_id == category_tree.c.id)
    )


def get_product_or_404(product_id: UUID, db: DBSession) -> Product:
    product = db.scalar(product_query().where(Product.id == product_id))
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


def replace_images(product: Product, image_payloads: list) -> None:
    product.images.clear()
    has_primary = any(image.is_primary for image in image_payloads)
    for index, image in enumerate(image_payloads):
        product.images.append(ProductImage(image_url=str(image.image_url), is_primary=image.is_primary or (index == 0 and not has_primary)))


@router.get("", response_model=ProductListResponse)
def list_products(
    db: DBSession,
    q: str | None = Query(default=None, min_length=1, max_length=255),
    category_id: UUID | None = None,
    gender: str | None = None,
    color: str | None = None,
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    sort: str = Query(default="newest", pattern="^(newest|price_asc|price_desc)$"),
    limit: int = Query(default=24, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ProductListResponse:
    statement = select(Product)
    if q:
        term = f"%{q.strip()}%"
        statement = statement.where(or_(Product.name.ilike(term), Product.description.ilike(term)))
    if category_id:
        category_tree = descendant_category_ids(category_id)
        statement = statement.where(Product.category_id.in_(select(category_tree.c.id)))
    if gender:
        statement = statement.where(Product.gender.ilike(gender.strip()))
    if color:
        statement = statement.where(Product.color.ilike(color.strip()))
    if min_price is not None:
        statement = statement.where(Product.price >= min_price)
    if max_price is not None:
        statement = statement.where(Product.price <= max_price)

    total = db.scalar(select(func.count()).select_from(statement.order_by(None).subquery())) or 0
    order_by = {"newest": Product.created_at.desc(), "price_asc": Product.price.asc(), "price_desc": Product.price.desc()}[sort]
    items_statement = statement.options(selectinload(Product.images), selectinload(Product.category))
    items = list(db.scalars(items_statement.order_by(order_by).limit(limit).offset(offset)).unique())
    return ProductListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/filters", response_model=FilterFacetsResponse)
def get_product_filters(db: DBSession) -> FilterFacetsResponse:
    colors = list(
        db.scalars(select(Product.color).distinct().where(Product.color.is_not(None)).order_by(Product.color))
    )
    genders = list(
        db.scalars(select(Product.gender).distinct().where(Product.gender.is_not(None)).order_by(Product.gender))
    )
    price_min, price_max = db.execute(select(func.min(Product.price), func.max(Product.price))).one()
    return FilterFacetsResponse(colors=colors, genders=genders, price=PriceRange(min=price_min, max=price_max))


@router.get("/{product_id}", response_model=ProductRead)
def get_product(product_id: UUID, db: DBSession) -> Product:
    return get_product_or_404(product_id, db)


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: DBSession, _: AdminUser) -> Product:
    if payload.category_id and db.get(Category, payload.category_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    product = Product(
        name=payload.name.strip(),
        description=payload.description,
        category_id=payload.category_id,
        gender=payload.gender,
        color=payload.color,
        price=payload.price,
    )
    replace_images(product, payload.images)
    db.add(product)
    db.commit()
    return get_product_or_404(product.id, db)


@router.patch("/{product_id}", response_model=ProductRead)
def update_product(product_id: UUID, payload: ProductUpdate, db: DBSession, _: AdminUser) -> Product:
    product = get_product_or_404(product_id, db)
    if payload.category_id and db.get(Category, payload.category_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    for field in ("name", "description", "category_id", "gender", "color", "price"):
        if field in payload.model_fields_set:
            value = getattr(payload, field)
            setattr(product, field, value.strip() if field == "name" and value else value)
    if payload.images is not None:
        replace_images(product, payload.images)
    db.commit()
    return get_product_or_404(product.id, db)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: UUID, db: DBSession, _: AdminUser) -> None:
    product = get_product_or_404(product_id, db)
    db.delete(product)
    db.commit()
