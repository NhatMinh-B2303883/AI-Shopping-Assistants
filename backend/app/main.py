from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings


def create_application() -> FastAPI:
    app = FastAPI(title=settings.app_name, version="0.1.0")
    
    CATALOG_IMAGES_DIR = Path("/data/products/images")
    if CATALOG_IMAGES_DIR.is_dir():
        app.mount(
            "/catalog-images",
            StaticFiles(directory=str(CATALOG_IMAGES_DIR)),
            name="catalog-images",
        )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.get("/health", tags=["health"])
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_application()
