from fastapi import APIRouter

from app.api.v1.endpoints import auth, categories, products, user_activity

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(user_activity.router, prefix="/users", tags=["user activity"])
