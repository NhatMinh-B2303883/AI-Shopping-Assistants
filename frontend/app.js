/**
 * EAST & SOUL — Modern Minimalist Shopping Assistant
 * Hỗ trợ tìm kiếm đa phương thức: Từ khóa, Ảnh AI, Quét mã QR
 */

// ── Dữ liệu 23 sản phẩm đồng bộ từ backend/scripts/seed.py ──
const PRODUCTS = [
  // ── Sneakers ────────────────────────────────────────────────────────────
  {
    id: "giay-1",
    code: "SEED-SHOES-01",
    category: "giay",
    subCategory: "Sneakers",
    label: "Sneaker",
    name: "Urban Runner X1",
    price: 850000,
    oldPrice: 1050000,
    tag: "Hot",
    colors: ["#e0e0e0", "#ffffff"],
    colorNames: ["Trắng xám", "Trắng"],
    image: "1549298916-b41d501d3772",
    description: "Giày sneaker cổ thấp thiết kế tối giản, đế cao su chống trượt, thích hợp đi phố hàng ngày.",
    rating: 4.8,
    reviews: 124
  },
  {
    id: "giay-2",
    code: "SEED-SHOES-02",
    category: "giay",
    subCategory: "Sneakers",
    label: "Sneaker",
    name: "Street Classic Pro",
    price: 1200000,
    oldPrice: 1450000,
    tag: "Bán chạy",
    colors: ["#212121", "#424242"],
    colorNames: ["Đen nhám", "Xám đen"],
    image: "1525966222134-fcfa99b8ae77",
    description: "Sneaker phong cách retro với phần upper bằng da tổng hợp cao cấp và đệm lót êm ái.",
    rating: 4.9,
    reviews: 89
  },
  {
    id: "giay-3",
    code: "SEED-SHOES-03",
    category: "giay",
    subCategory: "Sneakers",
    label: "Sneaker",
    name: "Neon Kick 2.0",
    price: 750000,
    oldPrice: 890000,
    tag: "Mới",
    colors: ["#f48fb1", "#ffffff"],
    colorNames: ["Hồng neon", "Trắng"],
    image: "1595950653106-6c9ebd614d3a",
    description: "Sneaker nổi bật với phối màu neon, thiết kế trẻ trung năng động.",
    rating: 4.7,
    reviews: 56
  },
  {
    id: "giay-4",
    code: "SEED-SHOES-04",
    category: "giay",
    subCategory: "Sneakers",
    label: "Sneaker",
    name: "Canvas Low Top",
    price: 550000,
    oldPrice: 650000,
    tag: "",
    colors: ["#1a237e", "#ffffff"],
    colorNames: ["Xanh navy", "Trắng"],
    image: "1607522370275-f14206abe5d3",
    description: "Giày vải canvas mềm nhẹ, thoáng khí, phù hợp mùa hè.",
    rating: 4.6,
    reviews: 42
  },
  {
    id: "giay-5",
    code: "SEED-SHOES-05",
    category: "giay",
    subCategory: "Sneakers",
    label: "Sneaker",
    name: "Monochrome Edge",
    price: 980000,
    oldPrice: 1150000,
    tag: "Xu hướng",
    colors: ["#fafafa", "#e0e0e0"],
    colorNames: ["Trắng đơn sắc", "Ghi sáng"],
    image: "1560769629-975ec94e6a86",
    description: "Sneaker toàn trắng đơn sắc, dễ phối đồ với mọi outfit.",
    rating: 4.9,
    reviews: 178
  },

  // ── Running Shoes ────────────────────────────────────────────────────────
  {
    id: "giay-6",
    code: "SEED-SHOES-06",
    category: "giay",
    subCategory: "Running Shoes",
    label: "Giày chạy bộ",
    name: "AeroStride 500",
    price: 1850000,
    oldPrice: 2150000,
    tag: "Cao cấp",
    colors: ["#1565c0", "#0d47a1"],
    colorNames: ["Xanh dương", "Xanh sẫm"],
    image: "1542291026-7eec264c27ff",
    description: "Giày chạy bộ với công nghệ đệm khí, hỗ trợ vòm chân, lý tưởng cho cự ly dài.",
    rating: 4.9,
    reviews: 210
  },
  {
    id: "giay-7",
    code: "SEED-SHOES-07",
    category: "giay",
    subCategory: "Running Shoes",
    label: "Giày chạy bộ",
    name: "FlexRun Lite",
    price: 1350000,
    oldPrice: 1590000,
    tag: "",
    colors: ["#ff7043", "#ffffff"],
    colorNames: ["Cam san hô", "Trắng"],
    image: "1584735935682-2f2b69dff9d2",
    description: "Giày chạy siêu nhẹ với đế Phylon linh hoạt, phù hợp tập gym và chạy ngắn.",
    rating: 4.8,
    reviews: 95
  },
  {
    id: "giay-8",
    code: "SEED-SHOES-08",
    category: "giay",
    subCategory: "Running Shoes",
    label: "Giày chạy bộ",
    name: "TrailBlazer Pro",
    price: 2100000,
    oldPrice: 2450000,
    tag: "Chống nước",
    colors: ["#757575", "#424242"],
    colorNames: ["Xám xi măng", "Đen"],
    image: "1551107696-a4b0c5a0d9a2",
    description: "Giày chạy địa hình với đế bám tốt, chống nước nhẹ, phù hợp chạy trail.",
    rating: 4.9,
    reviews: 134
  },
  {
    id: "giay-9",
    code: "SEED-SHOES-09",
    category: "giay",
    subCategory: "Running Shoes",
    label: "Giày chạy bộ",
    name: "SpeedForm Elite",
    price: 3200000,
    oldPrice: 3800000,
    tag: "Flagship",
    colors: ["#f9a825", "#212121"],
    colorNames: ["Vàng dạ quang", "Đen"],
    image: "1539185441755-769473a23570",
    description: "Giày thi đấu tốc độ cao với carbon plate và đệm foam phản lực.",
    rating: 5.0,
    reviews: 312
  },

  // ── Sandals ──────────────────────────────────────────────────────────────
  {
    id: "giay-10",
    code: "SEED-SHOES-10",
    category: "giay",
    subCategory: "Sandals",
    label: "Dép & Sandal",
    name: "Summer Slide Basic",
    price: 250000,
    oldPrice: 320000,
    tag: "Giá tốt",
    colors: ["#d7ccc8", "#8d6e63"],
    colorNames: ["Kem be", "Nâu nhạt"],
    image: "1562183241-b937e95585b6",
    description: "Dép xăng đan đế EVA nhẹ, quai ngang đơn giản, thoải mái cho mùa hè.",
    rating: 4.5,
    reviews: 68
  },
  {
    id: "giay-11",
    code: "SEED-SHOES-11",
    category: "giay",
    subCategory: "Sandals",
    label: "Dép & Sandal",
    name: "Sport Sandal Active",
    price: 480000,
    oldPrice: 580000,
    tag: "",
    colors: ["#6d4c41", "#3e2723"],
    colorNames: ["Nâu đất", "Đen đất"],
    image: "1603808033192-082d6919d3e1",
    description: "Dép thể thao với quai velcro điều chỉnh được, đế chống trượt, đi biển hoặc trekking nhẹ.",
    rating: 4.7,
    reviews: 51
  },

  // ── T-Shirt ──────────────────────────────────────────────────────────────
  {
    id: "ao-1",
    code: "SEED-CLOTH-01",
    category: "ao",
    subCategory: "T-Shirt",
    label: "Áo thun",
    name: "Essential Tee White",
    price: 199000,
    oldPrice: 250000,
    tag: "Basic",
    colors: ["#fafafa", "#e0e0e0"],
    colorNames: ["Trắng tinh", "Ghi nhạt"],
    image: "1521572267360-ee0c2909d518",
    description: "Áo thun basic cổ tròn 100% cotton, thoáng mát, form regular fit phù hợp mọi vóc dáng.",
    rating: 4.8,
    reviews: 245
  },
  {
    id: "ao-2",
    code: "SEED-CLOTH-02",
    category: "ao",
    subCategory: "T-Shirt",
    label: "Áo thun",
    name: "Graphic Print Tee",
    price: 320000,
    oldPrice: 390000,
    tag: "Streetwear",
    colors: ["#212121", "#424242"],
    colorNames: ["Đen hoạ tiết", "Ghi sẫm"],
    image: "1618354691373-d851c5c3a990",
    description: "Áo thun in họa tiết streetwear, chất liệu cotton blend 65/35 co giãn nhẹ.",
    rating: 4.7,
    reviews: 112
  },
  {
    id: "ao-3",
    code: "SEED-CLOTH-03",
    category: "ao",
    subCategory: "T-Shirt",
    label: "Áo thun",
    name: "Cropped Pastel Tee",
    price: 280000,
    oldPrice: 340000,
    tag: "",
    colors: ["#ce93d8", "#ffffff"],
    colorNames: ["Tím pastel", "Trắng"],
    image: "1583743814966-8936f5b7be1a",
    description: "Áo thun ngắn tay crop top màu pastel, form dáng năng động trẻ trung.",
    rating: 4.6,
    reviews: 73
  },
  {
    id: "ao-4",
    code: "SEED-CLOTH-04",
    category: "ao",
    subCategory: "T-Shirt",
    label: "Áo thun",
    name: "Oversized Drop Shoulder",
    price: 350000,
    oldPrice: 420000,
    tag: "Form rộng",
    colors: ["#9e9e9e", "#616161"],
    colorNames: ["Xám tiêu", "Xám đậm"],
    image: "1503342217505-b0a15ec3261c",
    description: "Áo thun tay lỡ form rộng phong cách unisex, vải cotton dày dặn.",
    rating: 4.8,
    reviews: 164
  },
  {
    id: "ao-5",
    code: "SEED-CLOTH-05",
    category: "ao",
    subCategory: "T-Shirt",
    label: "Áo thun",
    name: "Striped Nautical Tee",
    price: 260000,
    oldPrice: 320000,
    tag: "",
    colors: ["#283593", "#ffffff"],
    colorNames: ["Xanh sọc trắng", "Trắng sọc xanh"],
    image: "1523381210434-271e8be1f52b",
    description: "Áo thun kẻ sọc phong cách hải quân, co dãn 4 chiều, mặc thoải mái cả ngày.",
    rating: 4.7,
    reviews: 88
  },

  // ── Hoodie ───────────────────────────────────────────────────────────────
  {
    id: "ao-6",
    code: "SEED-CLOTH-06",
    category: "ao",
    subCategory: "Hoodie",
    label: "Áo Hoodie",
    name: "Classic Pullover Hoodie",
    price: 680000,
    oldPrice: 820000,
    tag: "Bán chạy",
    colors: ["#bdbdbd", "#424242"],
    colorNames: ["Xám nỉ", "Đen"],
    image: "1556905055-8f358a7a47b2",
    description: "Áo hoodie chui đầu chất nỉ bông dày ấm, túi kangaroo, dây rút mũ điều chỉnh.",
    rating: 4.9,
    reviews: 215
  },
  {
    id: "ao-7",
    code: "SEED-CLOTH-07",
    category: "ao",
    subCategory: "Hoodie",
    label: "Áo Hoodie",
    name: "Zip-Up Tech Fleece",
    price: 950000,
    oldPrice: 1150000,
    tag: "Tech Fleece",
    colors: ["#1a237e", "#000000"],
    colorNames: ["Xanh navy", "Đen"],
    image: "1578587018452-892bacefd3f2",
    description: "Áo hoodie kéo khóa chất liệu tech fleece cao cấp, giữ ấm tốt và thoáng khí.",
    rating: 4.9,
    reviews: 142
  },
  {
    id: "ao-8",
    code: "SEED-CLOTH-08",
    category: "ao",
    subCategory: "Hoodie",
    label: "Áo Hoodie",
    name: "Pastel Oversized Hoodie",
    price: 720000,
    oldPrice: 860000,
    tag: "",
    colors: ["#f8bbd0", "#ffffff"],
    colorNames: ["Hồng phấn", "Trắng kem"],
    image: "1509967419530-da38b4704bc6",
    description: "Áo hoodie form rộng màu pastel, chất cotton dày mềm mịn, phù hợp layer.",
    rating: 4.8,
    reviews: 91
  },

  // ── Jacket ───────────────────────────────────────────────────────────────
  {
    id: "ao-9",
    code: "SEED-CLOTH-09",
    category: "ao",
    subCategory: "Jacket",
    label: "Áo khoác",
    name: "Windbreaker Lightweight",
    price: 1100000,
    oldPrice: 1350000,
    tag: "Chống gió",
    colors: ["#212121", "#616161"],
    colorNames: ["Đen nhám", "Xám"],
    image: "1544441893-675973e31985",
    description: "Áo khoác gió siêu nhẹ có thể gấp gọn vào túi, chống nước mưa nhỏ.",
    rating: 4.8,
    reviews: 130
  },
  {
    id: "ao-10",
    code: "SEED-CLOTH-10",
    category: "ao",
    subCategory: "Jacket",
    label: "Áo khoác",
    name: "Bomber Satin Jacket",
    price: 1450000,
    oldPrice: 1750000,
    tag: "Phong cách",
    colors: ["#827717", "#1b5e20"],
    colorNames: ["Xanh rêu olive", "Xanh lục"],
    image: "1591047139829-d91aecb6caea",
    description: "Áo bomber vải satin bóng mịn, phối màu hai tông, cổ gân bo dệt.",
    rating: 4.9,
    reviews: 167
  },
  {
    id: "ao-11",
    code: "SEED-CLOTH-11",
    category: "ao",
    subCategory: "Jacket",
    label: "Áo khoác",
    name: "Denim Trucker Jacket",
    price: 1250000,
    oldPrice: 1500000,
    tag: "Vintage",
    colors: ["#1565c0", "#0d47a1"],
    colorNames: ["Xanh denim wash", "Xanh chàm"],
    image: "1576995853123-5a10305d93c0",
    description: "Áo khoác denim cổ điển kiểu trucker, wash màu trung tính dễ phối.",
    rating: 4.9,
    reviews: 198
  },
  {
    id: "ao-12",
    code: "SEED-CLOTH-12",
    category: "ao",
    subCategory: "Jacket",
    label: "Áo khoác",
    name: "Puffer Crop Jacket",
    price: 1350000,
    oldPrice: 1600000,
    tag: "Mùa đông",
    colors: ["#eceff1", "#b0bec5"],
    colorNames: ["Trắng tuyết", "Xám nhạt"],
    image: "1548883354-7622d03aca27",
    description: "Áo phao ngắn form crop, chất liệu nylon bóng nhẹ, giữ ấm mùa đông.",
    rating: 4.7,
    reviews: 84
  }
];

// ── Trạng thái ứng dụng ──
let currentCategory = "all";
let searchKeyword = "";
let currentSort = "default";
let maxPriceFilter = 3500000;
let currentPricePreset = "all"; // "all", "under500", "500-1500", "over1500", "custom"
let cart = [];
let appliedVoucher = null; // { code: "SOUL20", discountPercent: 20 }
const FREESHIP_THRESHOLD = 399000;

// QR Scanner state
let qrStream = null;
let qrScanActive = false;
let qrScanInterval = null;

// Tiện ích DOM & Định dạng
const $ = id => document.getElementById(id);
const formatVND = n => new Intl.NumberFormat("vi-VN", { style: "currency", currency: "VND" }).format(n);
const img = id => `https://images.unsplash.com/photo-${id}?auto=format&fit=crop&w=700&q=80`;

// ── Khởi tạo ──
document.addEventListener("DOMContentLoaded", () => {
  renderCatalog();
  setupImageDropzone();
  setupQrDropzone();
  setupGlobalKeys();
});

// Phím tắt bàn phím (Escape đóng modal, / tìm kiếm)
function setupGlobalKeys() {
  document.addEventListener("keydown", e => {
    if (e.key === "Escape") {
      closeQrScanModal();
      closeImageSearchModal();
      closeDetailModal();
      if ($("cart-drawer").classList.contains("open")) toggleCartDrawer();
    } else if (e.key === "/" && document.activeElement !== $("main-search-input")) {
      e.preventDefault();
      $("main-search-input").focus();
    }
  });
}

// Xử lý bộ lọc giá
function onPriceSliderInput(val) {
  maxPriceFilter = parseInt(val, 10);
  currentPricePreset = "custom";

  const display = $("price-max-display");
  if (display) display.textContent = formatVND(maxPriceFilter);

  document.querySelectorAll(".price-preset-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.pricePreset === "custom");
  });

  renderCatalog();
}

function setPricePreset(preset) {
  currentPricePreset = preset;

  document.querySelectorAll(".price-preset-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.pricePreset === preset);
  });

  const slider = $("price-range-input");
  const display = $("price-max-display");

  if (preset === "all") {
    maxPriceFilter = 3500000;
    if (slider) slider.value = 3500000;
    if (display) display.textContent = formatVND(3500000);
  } else if (preset === "under500") {
    maxPriceFilter = 500000;
    if (slider) slider.value = 500000;
    if (display) display.textContent = "< 500.000đ";
  } else if (preset === "500-1500") {
    maxPriceFilter = 1500000;
    if (slider) slider.value = 1500000;
    if (display) display.textContent = "500k – 1.5tr";
  } else if (preset === "over1500") {
    maxPriceFilter = 3500000;
    if (slider) slider.value = 3500000;
    if (display) display.textContent = "> 1.5tr";
  }

  renderCatalog();
}

function filterCategory(cat) {
  currentCategory = cat;
  renderCatalog();
}

function handleSearch(val) {
  searchKeyword = val || "";
  renderCatalog();
}

function sortCatalog(val) {
  currentSort = val || "default";
  renderCatalog();
}

function resetAll() {
  currentCategory = "all";
  searchKeyword = "";
  currentSort = "default";
  maxPriceFilter = 3500000;
  currentPricePreset = "all";

  const searchInput = $("main-search-input");
  if (searchInput) searchInput.value = "";

  const sortSelect = $("sort-select");
  if (sortSelect) sortSelect.value = "default";

  const slider = $("price-range-input");
  if (slider) slider.value = 3500000;

  const display = $("price-max-display");
  if (display) display.textContent = formatVND(3500000);

  document.querySelectorAll(".price-preset-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.pricePreset === "all");
  });

  renderCatalog();
}

// ==========================================================================
// RENDER DANH MỤC & SẢN PHẨM
// ==========================================================================
function renderCatalog() {
  let items = PRODUCTS.filter(p => currentCategory === "all" || p.category === currentCategory);

  // Lọc theo mức giá
  if (currentPricePreset === "under500") {
    items = items.filter(p => p.price < 500000);
  } else if (currentPricePreset === "500-1500") {
    items = items.filter(p => p.price >= 500000 && p.price <= 1500000);
  } else if (currentPricePreset === "over1500") {
    items = items.filter(p => p.price > 1500000);
  } else {
    items = items.filter(p => p.price <= maxPriceFilter);
  }
  
  const q = searchKeyword.trim().toLowerCase();
  if (q) {
    items = items.filter(p => 
      (p.name + " " + p.label + " " + (p.subCategory || "") + " " + p.description + " " + p.code).toLowerCase().includes(q)
    );
  }

  if (currentSort === "price-asc") items.sort((a, b) => a.price - b.price);
  if (currentSort === "price-desc") items.sort((a, b) => b.price - a.price);

  // Cập nhật số lượng trên các nút tab danh mục
  const totalAll = PRODUCTS.length;
  const totalAo = PRODUCTS.filter(p => p.category === "ao").length;
  const totalGiay = PRODUCTS.filter(p => p.category === "giay").length;

  if ($("count-all")) $("count-all").textContent = totalAll;
  if ($("count-ao")) $("count-ao").textContent = totalAo;
  if ($("count-giay")) $("count-giay").textContent = totalGiay;

  $("result-count").textContent = `${items.length} sản phẩm`;
  $("empty-state").classList.toggle("hidden", items.length > 0);

  // Sync nav buttons and catalog pill buttons
  document.querySelectorAll(".nav-item").forEach(b => {
    b.classList.toggle("active", b.dataset.cat === currentCategory);
  });
  document.querySelectorAll(".pill-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.catPill === currentCategory);
  });

  const grid = $("product-grid");
  grid.innerHTML = items.map(p => {
    const discountPercent = p.oldPrice ? Math.round((1 - p.price / p.oldPrice) * 100) : 0;
    return `
      <article class="card">
        <div class="thumb" onclick="openDetailModal('${p.id}')">
          <img src="${img(p.image)}" alt="${p.name}" loading="lazy">
          ${p.tag ? `<span class="tag">${p.tag}</span>` : ""}
          
          <!-- Nút mã QR góc ảnh -->
          <button class="card-qr-trigger" title="Xem mã QR sản phẩm" onclick="event.stopPropagation(); openProductQr('${p.id}')" aria-label="Xem mã QR">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="7" height="7"></rect>
              <rect x="14" y="3" width="7" height="7"></rect>
              <rect x="3" y="14" width="7" height="7"></rect>
              <path d="M14 14h3v3h-3z"></path>
              <path d="M20 14v3"></path>
              <path d="M14 20h6"></path>
            </svg>
          </button>

          <!-- Floating Action Bar on hover -->
          <div class="card-actions-bar">
            <button class="card-action-btn" onclick="event.stopPropagation(); openDetailModal('${p.id}')">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
              Xem chi tiết
            </button>
            <button class="card-action-btn" onclick="event.stopPropagation(); findSimilar('${p.category}')">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
              </svg>
              Tương tự
            </button>
          </div>
        </div>

        <div class="card-info">
          <span class="card-label">${p.label}</span>
          <h3 onclick="openDetailModal('${p.id}')">${p.name}</h3>

          <div class="dots" title="Màu sắc: ${p.colorNames.join(', ')}">
            ${p.colors.map(c => `<span class="dot" style="background:${c}"></span>`).join("")}
          </div>

          <div class="price-row">
            <span class="price">${formatVND(p.price)}</span>
            ${p.oldPrice ? `<span class="old-price">${formatVND(p.oldPrice)}</span>` : ""}
            ${discountPercent > 0 ? `<span class="discount-badge">-${discountPercent}%</span>` : ""}
          </div>
        </div>
      </article>
    `;
  }).join("");
}

function filterCategory(cat) {
  currentCategory = cat;
  renderCatalog();
}

function handleSearch(val) {
  searchKeyword = val;
  const indicator = $("filter-indicator");
  if (val.trim()) {
    indicator.classList.remove("hidden");
    $("filter-indicator-text").textContent = `Kết quả tìm kiếm cho: "${val}"`;
  } else {
    indicator.classList.add("hidden");
  }
  renderCatalog();
}

function resetAll() {
  searchKeyword = "";
  $("main-search-input").value = "";
  $("filter-indicator").classList.add("hidden");
  filterCategory("all");
  showToast("Đã đặt lại toàn bộ danh mục sản phẩm.");
}

function sortCatalog(val) {
  currentSort = val;
  renderCatalog();
}

function findSimilar(cat) {
  filterCategory(cat);
  showToast(`Đã lọc các sản phẩm cùng nhóm: ${cat.toUpperCase()}`);
  window.scrollTo({ top: 350, behavior: "smooth" });
}

// ==========================================================================
// TÍNH NĂNG: CHỤP ẢNH QUA ĐIỆN THOẠI (PHONE CAMERA SESSION)
// Flow: Web tạo QR → điện thoại quét → mở mobile-camera.html
//        → chụp ảnh → gửi về desktop → AI tìm sản phẩm tương đồng
// ==========================================================================

let phoneSessionId = null;
let phonePollInterval = null;
let phoneReceivedCategory = "ao";
let broadcastChannel = null;

function openQrScanModal() {
  $("modal-qr-scan").classList.remove("hidden");
  switchQrMode("phone");
}

function closeQrScanModal() {
  stopPhoneSession();
  $("modal-qr-scan").classList.add("hidden");
}

function switchQrMode(mode) {
  const isPhone = mode === "phone";
  const isUpload = mode === "upload";

  // Tab active states
  const tabPhone = $("qr-tab-phone");
  const tabUpload = $("qr-tab-upload");
  if (tabPhone) tabPhone.classList.toggle("active", isPhone);
  if (tabUpload) tabUpload.classList.toggle("active", isUpload);

  // Panel visibility
  const phoneView = $("qr-phone-view");
  const uploadView = $("qr-upload-view");
  if (phoneView) phoneView.classList.toggle("hidden", !isPhone);
  if (uploadView) uploadView.classList.toggle("hidden", !isUpload);

  if (isPhone) startPhoneSession();
  else stopPhoneSession();
}

// Tạo Session ID mới và sinh mã QR cho điện thoại quét
function startPhoneSession() {
  stopPhoneSession();

  // Sinh Session ID ngẫu nhiên 8 ký tự
  phoneSessionId = Math.random().toString(36).slice(2, 10).toUpperCase();

  // Hiển thị Session ID 
  const idEl = $("session-id-display");
  if (idEl) idEl.textContent = `Session: ${phoneSessionId}`;

  // Tạo URL trang mobile camera với session ID
  // Khi chạy qua HTTP server sẽ dùng đường dẫn thật.
  // Khi mở file:// local thì dùng đường dẫn tương đối.
  const baseUrl = window.location.origin + window.location.pathname.replace("index.html", "");
  const mobileUrl = baseUrl + `mobile-camera.html?session=${phoneSessionId}`;

  // Render mã QR vào #session-qr-render bằng qrcodejs
  const renderEl = $("session-qr-render");
  if (renderEl) {
    renderEl.innerHTML = ""; // Clear previous QR
    if (window.QRCode) {
      new QRCode(renderEl, {
        text: mobileUrl,
        width: 110,
        height: 110,
        colorDark: "#0f172a",
        colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.M
      });
    } else {
      // Fallback nếu thư viện chưa tải: SVG placeholder
      renderEl.innerHTML = generateCleanQrSvg(mobileUrl);
    }
  }

  // Reset về State A (waiting)
  const waiting = $("qr-phone-waiting");
  const received = $("qr-phone-received");
  if (waiting) waiting.classList.remove("hidden");
  if (received) received.classList.add("hidden");

  // Khởi lắng nghe tin nhắn từ điện thoại
  listenForPhonePhoto();
}

function stopPhoneSession() {
  if (phonePollInterval) { clearInterval(phonePollInterval); phonePollInterval = null; }
  if (broadcastChannel) { try { broadcastChannel.close(); } catch(e){} broadcastChannel = null; }
}

// Lắng nghe ảnh từ điện thoại qua BroadcastChannel + localStorage polling
function listenForPhonePhoto() {
  // 1. BroadcastChannel (same origin, same browser) — ưu tiên
  if (window.BroadcastChannel) {
    try {
      broadcastChannel = new BroadcastChannel("es_camera_sync");
      broadcastChannel.onmessage = (ev) => {
        const data = ev.data;
        if (data && data.sessionId === phoneSessionId && data.image) {
          onPhotoReceived(data);
        }
      };
    } catch(e) {}
  }

  // 2. localStorage polling (fallback cho local file://)
  phonePollInterval = setInterval(() => {
    try {
      const raw = localStorage.getItem("es_mobile_latest_event");
      if (!raw) return;
      const data = JSON.parse(raw);
      if (data && data.sessionId === phoneSessionId && data.image && !data._consumed) {
        data._consumed = true;
        localStorage.setItem("es_mobile_latest_event", JSON.stringify(data));
        onPhotoReceived(data);
      }
    } catch(e) {}
  }, 800);
}

// Nhận ảnh từ điện thoại — chuyển sang State B
function onPhotoReceived(data) {
  stopPhoneSession();
  phoneReceivedCategory = data.category || "ao";

  const imgEl = $("received-phone-img");
  if (imgEl) imgEl.src = data.image;

  const waiting = $("qr-phone-waiting");
  const received = $("qr-phone-received");
  if (waiting) waiting.classList.add("hidden");
  if (received) received.classList.remove("hidden");

  showToast("📸 Ảnh từ điện thoại đã nhận! Bấm 'Tìm sản phẩm' để xem gợi ý AI.");
}

// Áp dụng kết quả tìm kiếm từ ảnh nhận được
function applyPhotoSearch() {
  closeQrScanModal();
  filterCategory(phoneReceivedCategory);
  const catNames = { ao: "Áo nam", quan: "Quần nam", giay: "Giày & Sneaker" };
  showToast(`✨ AI đã phân tích ảnh. Hiển thị sản phẩm tương đồng: ${catNames[phoneReceivedCategory] || "Tất cả"}`);
  window.scrollTo({ top: 350, behavior: "smooth" });
}

// Đặt lại session để chụp lại
function resetPhoneSession() {
  startPhoneSession();
}

// Mở trang mobile camera ngay trên thiết bị hiện tại (thay thế)
function openMobileCameraLocal() {
  const sessionId = phoneSessionId || "local";
  const mobileUrl = "mobile-camera.html?session=" + sessionId;
  window.open(mobileUrl, "_blank");
}

// Tải ảnh QR lên từ máy (tab Upload)
function handleQrFileSelected(e) {
  if (e.target.files[0]) processUploadedFile(e.target.files[0]);
}

function setupQrDropzone() {
  const zone = $("qr-dropzone");
  if (!zone) return;
  ["dragenter", "dragover"].forEach(ev => {
    zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.add("over"); });
  });
  ["dragleave", "drop"].forEach(ev => {
    zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.remove("over"); });
  });
  zone.addEventListener("drop", ev => {
    if (ev.dataTransfer.files[0]) processUploadedFile(ev.dataTransfer.files[0]);
  });
}

// Demo nhanh mã QR mẫu sản phẩm (không cần camera thật)
function simulateQrScan(sampleCode) {
  closeQrScanModal();
  handleQrResult(sampleCode);
}

// Xử lý kết quả sau khi quét/nhập mã QR (sản phẩm hoặc voucher)
function handleQrResult(rawCode) {
  const text = (rawCode || "").trim();

  if (text.toUpperCase().includes("SOUL20") || text.toUpperCase().includes("VOUCHER")) {
    appliedVoucher = { code: "SOUL20", discountPercent: 20 };
    showToast("🎉 Quét QR thành công! Đã áp dụng Voucher giảm 20% (SOUL20).");
    toggleCartDrawer();
    return;
  }

  const found = PRODUCTS.find(p =>
    p.code.toLowerCase() === text.toLowerCase() ||
    p.id.toLowerCase() === text.toLowerCase() ||
    text.toLowerCase().includes(p.id)
  );

  if (found) {
    showToast(`✅ Đã tìm thấy sản phẩm: ${found.name}`);
    openDetailModal(found.id);
    return;
  }

  showToast(`🔍 Mã "${text}" — đang tìm kiếm...`);
  handleSearch(text);
}

// Mở modal chi tiết và cuộn đến phần QR card
function openProductQr(id) {
  openDetailModal(id);
  setTimeout(() => {
    const el = document.querySelector(".product-qr-card");
    if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
  }, 200);
}

// ==========================================================================
// TÍNH NĂNG: TÌM BẰNG HÌNH ẢNH (AI VISUAL SEARCH)
// ==========================================================================
function openImageSearchModal() {
  $("modal-image-search").classList.remove("hidden");
}

function closeImageSearchModal() {
  $("modal-image-search").classList.add("hidden");
}

function setupImageDropzone() {
  const zone = $("clean-dropzone");
  if (!zone) return;
  ["dragenter", "dragover"].forEach(e => zone.addEventListener(e, ev => { ev.preventDefault(); zone.classList.add("over"); }));
  ["dragleave", "drop"].forEach(e => zone.addEventListener(e, ev => { ev.preventDefault(); zone.classList.remove("over"); }));
  zone.addEventListener("drop", ev => { if (ev.dataTransfer.files[0]) processUploadedFile(ev.dataTransfer.files[0]); });
}

function handleFileSelected(e) {
  if (e.target.files[0]) processUploadedFile(e.target.files[0]);
}

function processUploadedFile(file) {
  closeImageSearchModal();
  const name = file.name.toLowerCase();
  let cat = "ao";
  if (/shoe|giay|sneaker|sandal/.test(name)) cat = "giay";
  else if (/pant|quan|jean|jogger|short/.test(name)) cat = "quan";
  
  filterCategory(cat);
  showToast(`✨ AI phân tích xong ảnh "${file.name}". Hiển thị sản phẩm tương đồng cao nhất.`);
  window.scrollTo({ top: 350, behavior: "smooth" });
}

function simulatePresetSearch(cat) {
  closeImageSearchModal();
  filterCategory(cat);
  const catNames = { ao: "Áo nam", quan: "Quần nam", giay: "Giày & Sneaker" };
  showToast(`✨ Đã lọc sản phẩm theo phong cách ảnh mẫu: ${catNames[cat] || cat}`);
  window.scrollTo({ top: 350, behavior: "smooth" });
}

// ==========================================================================
// MODAL CHI TIẾT SẢN PHẨM & SINH MÃ QR SẢN PHẨM SVG
// ==========================================================================
function openDetailModal(id) {
  const p = PRODUCTS.find(x => x.id === id);
  if (!p) return;

  const discountPercent = p.oldPrice ? Math.round((1 - p.price / p.oldPrice) * 100) : 0;
  const qrSvg = generateCleanQrSvg(p.code);

  $("detail-body").innerHTML = `
    <div class="detail-grid">
      <div class="detail-media">
        <img class="detail-main-img" src="${img(p.image)}" alt="${p.name}">
        ${p.tag ? `<span class="detail-badge-pill">${p.tag}</span>` : ""}
      </div>

      <div class="detail-content">
        <span class="detail-category">${p.label} · Mã: ${p.code}</span>
        <h2 class="detail-title">${p.name}</h2>

        <div class="detail-rating">
          <span class="stars">★★★★★</span>
          <strong>${p.rating}</strong>
          <span>(${p.reviews} lượt đánh giá)</span>
        </div>

        <div class="detail-price-box">
          <span class="detail-price">${formatVND(p.price)}</span>
          ${p.oldPrice ? `<span class="detail-old-price">${formatVND(p.oldPrice)}</span>` : ""}
          ${discountPercent > 0 ? `<span class="discount-badge">Tiết kiệm ${discountPercent}%</span>` : ""}
        </div>

        <p class="detail-desc">${p.description}</p>

        <!-- Kích thước -->
        <div class="option-label">
          <span>Kích thước:</span>
          <a href="#" onclick="showToast('Bảng size chuẩn form Regular fit Việt Nam'); return false;" style="font-size:0.75rem; text-decoration:underline; color:var(--text-muted);">Bảng quy đổi</a>
        </div>
        <div class="size-selector">
          <button class="size-btn" onclick="selectDetailSize(this)">S</button>
          <button class="size-btn active" onclick="selectDetailSize(this)">M</button>
          <button class="size-btn" onclick="selectDetailSize(this)">L</button>
          <button class="size-btn" onclick="selectDetailSize(this)">XL</button>
        </div>

        <!-- Màu sắc -->
        <div class="option-label">
          <span>Màu sắc: <strong>${p.colorNames[0]}</strong></span>
        </div>
        <div class="color-selector">
          ${p.colors.map((c, i) => `
            <span class="color-option ${i === 0 ? 'active' : ''}" style="background:${c}" title="${p.colorNames[i]}" onclick="selectDetailColor(this, '${p.colorNames[i]}')"></span>
          `).join("")}
        </div>

        <!-- Thao tác mua -->
        <div class="detail-actions">
          <button class="btn btn-primary btn-block" onclick="addToCart('${p.id}'); closeDetailModal();">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <path d="M16 10a4 4 0 0 1-8 0"></path>
            </svg>
            Thêm vào giỏ hàng
          </button>
          <button class="btn btn-ghost btn-block" onclick="findSimilar('${p.category}'); closeDetailModal();">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            </svg>
            Xem sản phẩm tương tự (AI Match)
          </button>
        </div>

        <!-- Thẻ mã QR sản phẩm -->
        <div class="product-qr-card">
          <div class="product-qr-svg-wrap">
            ${qrSvg}
          </div>
          <div class="product-qr-info">
            <span class="product-qr-title">Mã QR chính hãng: ${p.code}</span>
            <span class="product-qr-sub">Dùng camera quét tem QR tại cửa hàng để mở nhanh sản phẩm này trên web.</span>
          </div>
        </div>
      </div>
    </div>
  `;
  $("modal-detail").classList.remove("hidden");
}

function closeDetailModal() {
  $("modal-detail").classList.add("hidden");
}

function selectDetailSize(btn) {
  document.querySelectorAll(".size-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
}

function selectDetailColor(el, name) {
  document.querySelectorAll(".color-option").forEach(e => e.classList.remove("active"));
  el.classList.add("active");
  const label = el.closest(".detail-content").querySelector(".option-label strong");
  if (label) label.textContent = name;
}

// Bộ tạo SVG mã QR tối giản không phụ thuộc thư viện ngoài
function generateCleanQrSvg(code) {
  // Tạo matrix giả lập mã QR sắc nét chuẩn mực
  const seed = (code || "").split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);
  const size = 21;
  let rects = "";

  // 3 khối định vị góc (Corner Finder Patterns)
  const drawCorner = (ox, oy) => {
    rects += `<rect x="${ox}" y="${oy}" width="7" height="7" fill="#0f172a" rx="1.2"/>`;
    rects += `<rect x="${ox+1}" y="${oy+1}" width="5" height="5" fill="#ffffff" rx="0.8"/>`;
    rects += `<rect x="${ox+2}" y="${oy+2}" width="3" height="3" fill="#0f172a" rx="0.5"/>`;
  };
  drawCorner(0, 0);
  drawCorner(14, 0);
  drawCorner(0, 14);

  // Sinh các pixel ngẫu nhiên cố định theo seed để mã QR chân thực
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      if ((x < 8 && y < 8) || (x > 13 && y < 8) || (x < 8 && y > 13)) continue;
      // Thuật toán pseudo-hash
      const val = (Math.sin(seed * (x * 31 + y * 17)) * 10000) % 1;
      if (Math.abs(val) > 0.45) {
        rects += `<rect x="${x}" y="${y}" width="0.85" height="0.85" fill="#0f172a" rx="0.2"/>`;
      }
    }
  }

  return `
    <svg viewBox="-1 -1 23 23" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
      <rect x="-1" y="-1" width="23" height="23" fill="#ffffff"/>
      ${rects}
    </svg>
  `;
}

// ==========================================================================
// GIỎ HÀNG & THANH TOÁN (CART DRAWER)
// ==========================================================================
function toggleCartDrawer() {
  $("cart-drawer").classList.toggle("open");
  $("cart-backdrop").classList.toggle("hidden");
  renderCart();
}

function addToCart(id) {
  const product = PRODUCTS.find(p => p.id === id);
  if (!product) return;
  const existing = cart.find(c => c.product.id === id);
  if (existing) {
    existing.qty++;
  } else {
    cart.push({ product, qty: 1 });
  }
  updateCartBadge();
  showToast(`Đã thêm "${product.name}" vào giỏ hàng.`);
}

function updateCartQty(id, delta) {
  const item = cart.find(c => c.product.id === id);
  if (!item) return;
  item.qty += delta;
  if (item.qty <= 0) {
    cart = cart.filter(c => c.product.id !== id);
  }
  updateCartBadge();
  renderCart();
}

function removeFromCart(id) {
  cart = cart.filter(c => c.product.id !== id);
  updateCartBadge();
  renderCart();
  showToast("Đã xóa món đồ khỏi giỏ.");
}

function updateCartBadge() {
  const totalCount = cart.reduce((s, c) => s + c.qty, 0);
  $("cart-counter").textContent = totalCount;
  $("cart-count-sub").textContent = `${totalCount} món đồ`;
}

function renderCart() {
  const list = $("cart-items-list");
  const subtotal = cart.reduce((s, c) => s + c.product.price * c.qty, 0);
  
  // Thanh tiến độ Freeship
  const fillPct = Math.min(100, Math.round((subtotal / FREESHIP_THRESHOLD) * 100));
  $("shipping-progress-fill").style.width = `${fillPct}%`;
  if (subtotal >= FREESHIP_THRESHOLD) {
    $("shipping-progress-text").innerHTML = `🎉 Bạn đã đủ điều kiện được <strong>Miễn phí vận chuyển</strong>!`;
  } else {
    const diff = FREESHIP_THRESHOLD - subtotal;
    $("shipping-progress-text").textContent = `Thêm ${formatVND(diff)} để được Freeship toàn quốc!`;
  }

  // Danh sách giỏ hàng
  if (!cart.length) {
    list.innerHTML = `
      <div style="text-align:center; padding: 48px 0; color: var(--text-muted);">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom:12px; color:var(--text-subtle);">
          <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <path d="M16 10a4 4 0 0 1-8 0"></path>
        </svg>
        <p style="font-weight:600; color:var(--ink);">Giỏ hàng đang trống</p>
        <p style="font-size:0.85rem; margin-top:4px;">Hãy khám phá và chọn cho mình sản phẩm ưng ý.</p>
      </div>
    `;
    $("cart-subtotal-price").textContent = "0đ";
    $("cart-discount-row").classList.add("hidden");
    $("cart-total-price").textContent = "0đ";
    return;
  }

  list.innerHTML = cart.map(c => `
    <div class="cart-item">
      <img src="${img(c.product.image)}" alt="${c.product.name}">
      <div class="cart-item-details">
        <div class="cart-item-title">${c.product.name}</div>
        <div class="cart-item-price">${formatVND(c.product.price)}</div>
        
        <div class="cart-item-ctrls">
          <div class="qty-stepper">
            <button class="qty-btn" onclick="updateCartQty('${c.product.id}', -1)" aria-label="Giảm">&minus;</button>
            <span class="qty-val">${c.qty}</span>
            <button class="qty-btn" onclick="updateCartQty('${c.product.id}', 1)" aria-label="Tăng">&plus;</button>
          </div>
          <button class="cart-remove-btn" onclick="removeFromCart('${c.product.id}')">Xóa</button>
        </div>
      </div>
    </div>
  `).join("");

  $("cart-subtotal-price").textContent = formatVND(subtotal);

  // Tính Voucher
  let discount = 0;
  if (appliedVoucher) {
    discount = Math.round((subtotal * appliedVoucher.discountPercent) / 100);
    $("cart-discount-row").classList.remove("hidden");
    $("cart-discount-price").textContent = `-${formatVND(discount)}`;
  } else {
    $("cart-discount-row").classList.add("hidden");
  }

  const finalTotal = Math.max(0, subtotal - discount);
  $("cart-total-price").textContent = formatVND(finalTotal);
}

// Áp dụng mã Voucher
function applyPromoCode() {
  const input = $("promo-input");
  const code = (input.value || "").trim().toUpperCase();
  if (code === "SOUL20") {
    appliedVoucher = { code: "SOUL20", discountPercent: 20 };
    $("promo-applied-tag").classList.remove("hidden");
    input.value = "";
    renderCart();
    showToast("Đã áp dụng mã SOUL20: Giảm 20% tổng đơn!");
  } else if (!code) {
    showToast("Vui lòng nhập mã giảm giá.");
  } else {
    showToast(`Mã "${code}" không hợp lệ hoặc đã hết hạn.`);
  }
}

function removePromoCode() {
  appliedVoucher = null;
  $("promo-applied-tag").classList.add("hidden");
  renderCart();
  showToast("Đã gỡ bỏ mã giảm giá.");
}

function handleCheckout() {
  if (!cart.length) {
    showToast("Giỏ hàng đang trống. Vui lòng chọn sản phẩm.");
    return;
  }
  const total = $("cart-total-price").textContent;
  cart = [];
  appliedVoucher = null;
  $("promo-applied-tag").classList.add("hidden");
  updateCartBadge();
  renderCart();
  toggleCartDrawer();
  showToast(`🎉 Đặt hàng thành công (${total})! EAST & SOUL sẽ liên hệ giao hàng trong 2h.`);
}

// ==========================================================================
// THÔNG BÁO TOAST
// ==========================================================================
function showToast(msg) {
  const box = $("toast-box");
  const t = document.createElement("div");
  t.className = "toast";
  t.innerHTML = `
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
      <polyline points="22 4 12 14.01 9 11.01"></polyline>
    </svg>
    <span>${msg}</span>
  `;
  box.appendChild(t);
  setTimeout(() => {
    t.style.opacity = "0";
    t.style.transform = "translateY(8px)";
    t.style.transition = "all 0.3s ease-out";
    setTimeout(() => t.remove(), 300);
  }, 3200);
}