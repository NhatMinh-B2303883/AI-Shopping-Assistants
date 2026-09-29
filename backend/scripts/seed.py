"""Seed database with sample categories, products, and users.

Run from the backend container:
    docker compose exec backend python scripts/seed.py

The script is idempotent — running it multiple times will NOT create
duplicate records (it checks by name/email before inserting).
"""

from decimal import Decimal

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.category import Category
from app.models.product import Product, ProductImage
from app.models.user import User, UserRole

# ---------------------------------------------------------------------------
# Seed data definitions
# ---------------------------------------------------------------------------

CATEGORIES: list[dict] = [
    {"name": "Shoes", "parent": None},
    {"name": "Sneakers", "parent": "Shoes"},
    {"name": "Running Shoes", "parent": "Shoes"},
    {"name": "Sandals", "parent": "Shoes"},
    {"name": "Clothing", "parent": None},
    {"name": "T-Shirt", "parent": "Clothing"},
    {"name": "Hoodie", "parent": "Clothing"},
    {"name": "Jacket", "parent": "Clothing"},
]

# Placeholder image base URL — 400×500 portrait, neutral grey background
def _img(color_hex: str, label: str) -> str:
    label_encoded = label.replace(" ", "+")
    return f"https://placehold.co/400x500/{color_hex}/ffffff?text={label_encoded}"


PRODUCTS: list[dict] = [
    # ── Sneakers ────────────────────────────────────────────────────────────
    {
        "name": "Urban Runner X1",
        "description": "Giày sneaker cổ thấp thiết kế tối giản, đế cao su chống trượt, thích hợp đi phố hàng ngày.",
        "category": "Sneakers",
        "gender": "unisex",
        "color": "white",
        "price": Decimal("850000"),
        "image_color": "e0e0e0",
    },
    {
        "name": "Street Classic Pro",
        "description": "Sneaker phong cách retro với phần upper bằng da tổng hợp cao cấp và đệm lót êm ái.",
        "category": "Sneakers",
        "gender": "male",
        "color": "black",
        "price": Decimal("1200000"),
        "image_color": "212121",
    },
    {
        "name": "Neon Kick 2.0",
        "description": "Sneaker nổi bật với phối màu neon, thiết kế trẻ trung năng động.",
        "category": "Sneakers",
        "gender": "female",
        "color": "pink",
        "price": Decimal("750000"),
        "image_color": "f48fb1",
    },
    {
        "name": "Canvas Low Top",
        "description": "Giày vải canvas mềm nhẹ, thoáng khí, phù hợp mùa hè.",
        "category": "Sneakers",
        "gender": "unisex",
        "color": "navy",
        "price": Decimal("550000"),
        "image_color": "1a237e",
    },
    {
        "name": "Monochrome Edge",
        "description": "Sneaker toàn trắng đơn sắc, dễ phối đồ với mọi outfit.",
        "category": "Sneakers",
        "gender": "male",
        "color": "white",
        "price": Decimal("980000"),
        "image_color": "fafafa",
    },
    # ── Running Shoes ────────────────────────────────────────────────────────
    {
        "name": "AeroStride 500",
        "description": "Giày chạy bộ với công nghệ đệm khí, hỗ trợ vòm chân, lý tưởng cho cự ly dài.",
        "category": "Running Shoes",
        "gender": "male",
        "color": "blue",
        "price": Decimal("1850000"),
        "image_color": "1565c0",
    },
    {
        "name": "FlexRun Lite",
        "description": "Giày chạy siêu nhẹ với đế Phylon linh hoạt, phù hợp tập gym và chạy ngắn.",
        "category": "Running Shoes",
        "gender": "female",
        "color": "coral",
        "price": Decimal("1350000"),
        "image_color": "ff7043",
    },
    {
        "name": "TrailBlazer Pro",
        "description": "Giày chạy địa hình với đế bám tốt, chống nước nhẹ, phù hợp chạy trail.",
        "category": "Running Shoes",
        "gender": "male",
        "color": "grey",
        "price": Decimal("2100000"),
        "image_color": "757575",
    },
    {
        "name": "SpeedForm Elite",
        "description": "Giày thi đấu tốc độ cao với carbon plate và đệm foam phản lực.",
        "category": "Running Shoes",
        "gender": "unisex",
        "color": "yellow",
        "price": Decimal("3200000"),
        "image_color": "f9a825",
    },
    # ── Sandals ──────────────────────────────────────────────────────────────
    {
        "name": "Summer Slide Basic",
        "description": "Dép xăng đan đế EVA nhẹ, quai ngang đơn giản, thoải mái cho mùa hè.",
        "category": "Sandals",
        "gender": "unisex",
        "color": "beige",
        "price": Decimal("250000"),
        "image_color": "d7ccc8",
    },
    {
        "name": "Sport Sandal Active",
        "description": "Dép thể thao với quai velcro điều chỉnh được, đế chống trượt, đi biển hoặc trekking nhẹ.",
        "category": "Sandals",
        "gender": "male",
        "color": "brown",
        "price": Decimal("480000"),
        "image_color": "6d4c41",
    },
    # ── T-Shirt ──────────────────────────────────────────────────────────────
    {
        "name": "Essential Tee White",
        "description": "Áo thun basic cổ tròn 100% cotton, thoáng mát, form regular fit phù hợp mọi vóc dáng.",
        "category": "T-Shirt",
        "gender": "unisex",
        "color": "white",
        "price": Decimal("199000"),
        "image_color": "fafafa",
    },
    {
        "name": "Graphic Print Tee",
        "description": "Áo thun in họa tiết streetwear, chất liệu cotton blend 65/35 co giãn nhẹ.",
        "category": "T-Shirt",
        "gender": "male",
        "color": "black",
        "price": Decimal("320000"),
        "image_color": "212121",
    },
    {
        "name": "Cropped Pastel Tee",
        "description": "Áo thun ngắn tay crop top màu pastel, form dáng năng động trẻ trung.",
        "category": "T-Shirt",
        "gender": "female",
        "color": "lavender",
        "price": Decimal("280000"),
        "image_color": "ce93d8",
    },
    {
        "name": "Oversized Drop Shoulder",
        "description": "Áo thun tay lỡ form rộng phong cách unisex, vải cotton dày dặn.",
        "category": "T-Shirt",
        "gender": "unisex",
        "color": "grey",
        "price": Decimal("350000"),
        "image_color": "9e9e9e",
    },
    {
        "name": "Striped Nautical Tee",
        "description": "Áo thun kẻ sọc phong cách hải quân, co dãn 4 chiều, mặc thoải mái cả ngày.",
        "category": "T-Shirt",
        "gender": "unisex",
        "color": "navy",
        "price": Decimal("260000"),
        "image_color": "283593",
    },
    # ── Hoodie ───────────────────────────────────────────────────────────────
    {
        "name": "Classic Pullover Hoodie",
        "description": "Áo hoodie chui đầu chất nỉ bông dày ấm, túi kangaroo, dây rút mũ điều chỉnh.",
        "category": "Hoodie",
        "gender": "unisex",
        "color": "grey",
        "price": Decimal("680000"),
        "image_color": "bdbdbd",
    },
    {
        "name": "Zip-Up Tech Fleece",
        "description": "Áo hoodie kéo khóa chất liệu tech fleece cao cấp, giữ ấm tốt và thoáng khí.",
        "category": "Hoodie",
        "gender": "male",
        "color": "navy",
        "price": Decimal("950000"),
        "image_color": "1a237e",
    },
    {
        "name": "Pastel Oversized Hoodie",
        "description": "Áo hoodie form rộng màu pastel, chất cotton dày mềm mịn, phù hợp layer.",
        "category": "Hoodie",
        "gender": "female",
        "color": "pink",
        "price": Decimal("720000"),
        "image_color": "f8bbd0",
    },
    # ── Jacket ───────────────────────────────────────────────────────────────
    {
        "name": "Windbreaker Lightweight",
        "description": "Áo khoác gió siêu nhẹ có thể gấp gọn vào túi, chống nước mưa nhỏ.",
        "category": "Jacket",
        "gender": "unisex",
        "color": "black",
        "price": Decimal("1100000"),
        "image_color": "212121",
    },
    {
        "name": "Bomber Satin Jacket",
        "description": "Áo bomber vải satin bóng mịn, phối màu hai tông, cổ gân bo dệt.",
        "category": "Jacket",
        "gender": "male",
        "color": "olive",
        "price": Decimal("1450000"),
        "image_color": "827717",
    },
    {
        "name": "Denim Trucker Jacket",
        "description": "Áo khoác denim cổ điển kiểu trucker, wash màu trung tính dễ phối.",
        "category": "Jacket",
        "gender": "unisex",
        "color": "blue",
        "price": Decimal("1250000"),
        "image_color": "1565c0",
    },
    {
        "name": "Puffer Crop Jacket",
        "description": "Áo phao ngắn form crop, chất liệu nylon bóng nhẹ, giữ ấm mùa đông.",
        "category": "Jacket",
        "gender": "female",
        "color": "white",
        "price": Decimal("1350000"),
        "image_color": "eceff1",
    },
]

USERS: list[dict] = [
    {
        "name": "Nguyen Van An",
        "email": "an.nguyen@example.com",
        "password": "User123!",
    },
    {
        "name": "Tran Thi Bich",
        "email": "bich.tran@example.com",
        "password": "User123!",
    },
]

# ---------------------------------------------------------------------------
# Seeding logic
# ---------------------------------------------------------------------------


def seed_categories(db) -> dict[str, Category]:
    """Insert categories if they don't exist. Returns name → Category map."""
    cat_map: dict[str, Category] = {}

    # First pass: insert root categories
    for item in CATEGORIES:
        if item["parent"] is not None:
            continue
        existing = db.scalar(select(Category).where(Category.name == item["name"]))
        if existing:
            cat_map[item["name"]] = existing
        else:
            cat = Category(name=item["name"])
            db.add(cat)
            db.flush()  # get generated id
            cat_map[item["name"]] = cat
            print(f"  [+] Category: {item['name']}")

    # Second pass: insert child categories
    for item in CATEGORIES:
        if item["parent"] is None:
            continue
        parent = cat_map.get(item["parent"])
        existing = db.scalar(select(Category).where(Category.name == item["name"]))
        if existing:
            cat_map[item["name"]] = existing
        else:
            cat = Category(name=item["name"], parent_id=parent.id if parent else None)
            db.add(cat)
            db.flush()
            cat_map[item["name"]] = cat
            print(f"  [+] Category: {item['name']} (parent: {item['parent']})")

    return cat_map


def seed_products(db, cat_map: dict[str, Category]) -> int:
    """Insert products if they don't exist (checked by name). Returns count inserted."""
    inserted = 0
    for item in PRODUCTS:
        existing = db.scalar(select(Product).where(Product.name == item["name"]))
        if existing:
            continue

        category = cat_map.get(item["category"])
        product = Product(
            name=item["name"],
            description=item["description"],
            category_id=category.id if category else None,
            gender=item["gender"],
            color=item["color"],
            price=item["price"],
        )
        image_url = _img(item["image_color"], item["name"])
        product.images.append(ProductImage(image_url=image_url, is_primary=True))
        db.add(product)
        inserted += 1
        print(f"  [+] Product: {item['name']} ({item['color']}, {item['gender']}) — {item['price']:,}đ")

    return inserted


def seed_users(db) -> int:
    """Insert regular users if they don't exist. Returns count inserted."""
    inserted = 0
    for item in USERS:
        existing = db.scalar(select(User).where(User.email == item["email"]))
        if existing:
            print(f"  [~] User already exists: {item['email']}")
            continue
        user = User(
            name=item["name"],
            email=item["email"],
            password_hash=hash_password(item["password"]),
            role=UserRole.USER,
        )
        db.add(user)
        inserted += 1
        print(f"  [+] User: {item['name']} <{item['email']}>")
    return inserted


def main() -> None:
    print("=" * 60)
    print("  AI Shopping Assistants — Database Seeder")
    print("=" * 60)

    db = SessionLocal()
    try:
        print("\n▶ Seeding categories...")
        cat_map = seed_categories(db)

        print("\n▶ Seeding products...")
        n_products = seed_products(db, cat_map)

        print("\n▶ Seeding users...")
        n_users = seed_users(db)

        db.commit()

        print("\n" + "=" * 60)
        print(f"  Done! Inserted {n_products} product(s), {n_users} user(s).")
        print("=" * 60)
    except Exception as exc:
        db.rollback()
        print(f"\n[ERROR] Seed failed, rolled back: {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
