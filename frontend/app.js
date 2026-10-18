/**
 * EAST & SOUL — Modern Minimalist Shopping Assistant
 * Hỗ trợ tìm kiếm đa phương thức: Từ khóa, AI Image, AI Multimodal, Quét mã QR
 * Tuân thủ đầy đủ Hợp đồng tích hợp Backend FastAPI & AI SigLIP 2
 */

// ==========================================================================
// 1. CẤU HÌNH API & QUY ƯỚC URL ẢNH (Mục 1 & 6)
// ==========================================================================
const _curHost = (window.location && window.location.hostname) ? window.location.hostname : "localhost";
const CONFIG = {
  API_BASE_URL: `http://${_curHost}:8000`,
  API_V1_URL: `http://${_curHost}:8000/api/v1`,
  PLACEHOLDER_IMAGE: "images/product-placeholder.png",
  MAX_UPLOAD_BYTES: 10 * 1024 * 1024, // 10 MB
  ALLOWED_IMAGE_TYPES: ["image/jpeg", "image/png", "image/webp"],
  DEFAULT_PAGE_SIZE: 12
};


/**
 * Ghép URL tương đối với domain backend trước khi hiển thị (Mục 1.2)
 * @param {string|null|undefined} path - Đường dẫn ảnh từ API
 * @returns {string} URL hợp lệ
 */
function resolveImageUrl(path) {
  if (!path) return CONFIG.PLACEHOLDER_IMAGE;
  if (/^https?:\/\//i.test(path)) return path;
  return `${CONFIG.API_BASE_URL}/${path.replace(/^\/+/, "")}`;
}

/**
 * Xử lý an toàn giá sản phẩm có thể null/undefined (Mục 2)
 * @param {number|string|null|undefined} price 
 * @returns {string} Chuỗi hiển thị giá đã định dạng hoặc "Đang cập nhật"
 */
function formatProductPrice(price) {
  if (price === null || price === undefined || price === "" || isNaN(Number(price))) {
    return "Đang cập nhật";
  }
  return `${Number(price).toLocaleString("vi-VN")} đ`;
}

// Bảng ánh xạ tên màu ra mã hex để hiển thị chấm màu
const COLOR_HEX = {
  white: "#ffffff", black: "#18181b", pink: "#f472b6", navy: "#1e3a8a",
  blue: "#2563eb", coral: "#fb7185", grey: "#9ca3af", gray: "#9ca3af",
  yellow: "#eab308", beige: "#d6d3d1", brown: "#78350f", lavender: "#c084fc",
  olive: "#65a30d", green: "#16a34a", red: "#dc2626", orange: "#ea580c"
};

// ==========================================================================
// TRẠNG THÁI ỨNG DỤNG TOÀN CỤC
// ==========================================================================
let appState = {
  // Bộ lọc danh mục
  q: "",
  categoryId: null, // UUID hoặc null
  gender: "",
  color: "",
  colorsExpanded: false,
  minPrice: null,
  maxPrice: null,
  pricePreset: "all",
  sort: "newest", // "newest", "price_asc", "price_desc"
  limit: CONFIG.DEFAULT_PAGE_SIZE,
  offset: 0,
  total: 0,

  // Dữ liệu từ Backend
  products: [],
  categories: [],
  categoryById: {},
  filters: { colors: [], genders: [], price: { min: null, max: null } },

  // Chế độ tìm kiếm: "catalog" hoặc "ai"
  activeMode: "catalog",
  aiResults: [],
  aiMeta: null, // { type: 'image' | 'multimodal', query: '', weight: 0.5, total: 0 }

  // Modal tìm kiếm AI
  aiSelectedFile: null,
  aiSearchMode: "visual", // "visual" hoặc "multimodal"
  aiWeight: 0.5,

  // Xác thực người dùng (Mục 5)
  token: localStorage.getItem("es_auth_token") || null,
  currentUser: null,

  // Giỏ hàng & Voucher
  cart: [],
  appliedVoucher: null,

  // Trạng thái tải
  isLoading: false
};

const FREESHIP_THRESHOLD = 399000;
const $ = id => document.getElementById(id);

// ==========================================================================
// KHỞI TẠO ỨNG DỤNG
// ==========================================================================
document.addEventListener("DOMContentLoaded", async () => {
  setupGlobalKeys();
  setupImageDropzone();
  setupQrDropzone();
  checkAuthSession();

  // Tải đồng thời Categories và Filters từ backend trước khi tải danh sách sản phẩm
  await Promise.allSettled([
    loadCategories(),
    loadFilters()
  ]);

  loadProducts();

  // Đóng dropdown tài khoản khi click ngoài
  document.addEventListener("click", e => {
    const wrap = $("user-trigger-wrap");
    const menu = $("user-dropdown-menu");
    if (wrap && menu && !wrap.contains(e.target)) {
      menu.classList.add("hidden");
    }
  });
});

function setupGlobalKeys() {
  document.addEventListener("keydown", e => {
    if (e.key === "Escape") {
      closeQrScanModal();
      closeImageSearchModal();
      closeDetailModal();
      closeAuthModal();
      if ($("cart-drawer").classList.contains("open")) toggleCartDrawer();
      const menu = $("user-dropdown-menu");
      if (menu) menu.classList.add("hidden");
    } else if (e.key === "/" && document.activeElement !== $("main-search-input")) {
      e.preventDefault();
      $("main-search-input").focus();
    }
  });
}

// ==========================================================================
// 2. TẢI DỮ LIỆU TỪ BACKEND FASTAPI (Mục 4)
// ==========================================================================

/**
 * Tải danh mục sản phẩm từ GET /api/v1/categories
 */
async function loadCategories() {
  try {
    const res = await fetch(`${CONFIG.API_V1_URL}/categories`);
    if (!res.ok) throw new Error("Không thể tải danh mục");
    const data = await res.json();
    appState.categories = data;
    appState.categoryById = Object.fromEntries(data.map(c => [c.id, c]));
  } catch (err) {
    console.warn("Chưa kết nối được API categories:", err.message);
  }
}

/**
 * Tải facet bộ lọc từ GET /api/v1/products/filters (Mục 4.2)
 */
async function loadFilters() {
  try {
    const res = await fetch(`${CONFIG.API_V1_URL}/products/filters`);
    if (!res.ok) throw new Error("Không thể tải bộ lọc");
    const data = await res.json();
    appState.filters = data;
    renderDynamicFacets(data);
  } catch (err) {
    console.warn("Chưa kết nối được API filters:", err.message);
  }
}

/**
 * Hiển thị các facet động (Giới tính, Màu sắc, Khoảng giá) lên giao diện
 */
function renderDynamicFacets(filters) {
  // 1. Cập nhật giới tính
  const genderSelect = $("gender-filter-select");
  if (genderSelect && filters.genders && filters.genders.length > 0) {
    const options = [`<option value="">Tất cả giới tính</option>`];
    filters.genders.forEach(g => {
      const label = g.toLowerCase() === "men" ? "Nam" : (g.toLowerCase() === "women" ? "Nữ" : g);
      options.push(`<option value="${g}">${label}</option>`);
    });
    genderSelect.innerHTML = options.join("");
  }

  // 2. Cập nhật màu sắc (Mặc định 8 màu, hỗ trợ mở rộng/thu gọn)
  const colorsList = $("facet-colors-list");
  if (colorsList && filters.colors && filters.colors.length > 0) {
    const allColors = filters.colors;
    const MAX_DEFAULT = 8;
    let visibleColors = allColors;
    const isExpandable = allColors.length > MAX_DEFAULT;
    let hiddenCount = 0;

    if (isExpandable && !appState.colorsExpanded) {
      // Lấy 8 màu đầu tiên
      visibleColors = allColors.slice(0, MAX_DEFAULT);

      // Màu đang được chọn luôn hiện, kể cả khi nằm ngoài 8 màu đầu
      if (appState.color) {
        const isSelectedVisible = visibleColors.some(
          c => c.toLowerCase() === appState.color.toLowerCase()
        );
        if (!isSelectedVisible) {
          const selectedColor = allColors.find(
            c => c.toLowerCase() === appState.color.toLowerCase()
          );
          if (selectedColor) {
            visibleColors.push(selectedColor);
          }
        }
      }

      hiddenCount = allColors.length - visibleColors.length;
    }

    let pillsHtml = visibleColors.map(col => {
      const hex = COLOR_HEX[col.toLowerCase()] || "#94a3b8";
      const isActive = appState.color && appState.color.toLowerCase() === col.toLowerCase();
      return `
        <button class="facet-color-pill ${isActive ? 'active' : ''}" onclick="toggleColorFilter('${col}')" title="Lọc màu ${col}">
          <span class="facet-color-dot" style="background:${hex};"></span>
          <span>${col}</span>
        </button>
      `;
    }).join("");

    if (isExpandable) {
      if (!appState.colorsExpanded && hiddenCount > 0) {
        pillsHtml += `
          <button class="facet-color-more-btn" onclick="toggleColorsExpanded()" title="Xem thêm ${hiddenCount} màu khác">
            +${hiddenCount} màu
          </button>
        `;
      } else if (appState.colorsExpanded) {
        pillsHtml += `
          <button class="facet-color-more-btn" onclick="toggleColorsExpanded()" title="Thu gọn danh sách màu">
            Thu gọn &laquo;
          </button>
        `;
      }
    }

    colorsList.innerHTML = pillsHtml;
  }


  // 3. Cập nhật thanh trượt giá tối đa nếu backend có giá trị
  if (filters.price && filters.price.max != null) {
    const maxVal = Math.ceil(Number(filters.price.max));
    const slider = $("price-range-input");
    if (slider) {
      slider.max = maxVal;
      if (appState.maxPrice == null || appState.maxPrice > maxVal) {
        appState.maxPrice = maxVal;
        slider.value = maxVal;
        if ($("price-max-display")) $("price-max-display").textContent = formatProductPrice(maxVal);
      }
    }
  }
}

/**
 * Lấy danh sách sản phẩm từ backend với phân trang và bộ lọc (Mục 4.1)
 * GET /api/v1/products?q=...&category_id=...&gender=...&color=...&min_price=...&max_price=...&sort=...&limit=...&offset=...
 */
async function loadProducts(resetOffset = false) {
  if (resetOffset) {
    appState.offset = 0;
  }

  // Nếu đang xem kết quả tìm kiếm AI thì hiển thị trực tiếp kết quả AI
  if (appState.activeMode === "ai") {
    renderAiResults();
    return;
  }

  setLoadingGrid(true);

  try {
    const params = new URLSearchParams();
    if (appState.q.trim()) params.set("q", appState.q.trim());
    if (appState.categoryId) params.set("category_id", appState.categoryId);
    if (appState.gender) params.set("gender", appState.gender);
    if (appState.color) params.set("color", appState.color);
    if (appState.minPrice != null) params.set("min_price", appState.minPrice);
    if (appState.maxPrice != null) params.set("max_price", appState.maxPrice);
    if (appState.sort) params.set("sort", appState.sort);
    params.set("limit", appState.limit);
    params.set("offset", appState.offset);

    const res = await fetch(`${CONFIG.API_V1_URL}/products?${params.toString()}`);
    if (!res.ok) throw new Error(`Lỗi API: ${res.status}`);

    const data = await res.json();
    appState.products = data.items || [];
    appState.total = data.total || 0;
    appState.limit = data.limit || CONFIG.DEFAULT_PAGE_SIZE;
    appState.offset = data.offset || 0;

    renderCatalog();
    renderPagination();
  } catch (err) {
    console.error("Lỗi tải sản phẩm:", err);
    $("product-grid").innerHTML = `
      <div class="loading-block" style="grid-column: 1 / -1; padding: 40px 10px;">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" style="margin-bottom:12px;">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <p style="font-weight:600; color:var(--ink);">Không thể tải danh sách sản phẩm</p>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-top:4px;">
          Hãy kiểm tra backend FastAPI đã khởi động tại <code>${CONFIG.API_BASE_URL}</code>.
        </p>
        <button class="btn btn-sm btn-primary" onclick="loadProducts()" style="margin-top:14px;">Thử lại</button>
      </div>
    `;
    $("result-count").textContent = "0 sản phẩm";
    $("empty-state").classList.add("hidden");
    $("pagination-wrap").classList.add("hidden");
  } finally {
    setLoadingGrid(false);
  }
}

function setLoadingGrid(isLoading) {
  appState.isLoading = isLoading;
  const grid = $("product-grid");
  if (isLoading && (!appState.products || appState.products.length === 0)) {
    grid.innerHTML = `
      <div class="loading-block" style="grid-column: 1 / -1; padding: 60px 0;">
        <span class="spinner" style="border-color: rgba(15, 23, 42, 0.2); border-top-color: var(--ink); width:28px; height:28px;"></span>
        <p style="margin-top:14px; font-weight:500;">Đang kết nối cơ sở dữ liệu sản phẩm...</p>
      </div>
    `;
  }
}

// ==========================================================================
// 3. RENDER CATALOG & THẺ SẢN PHẨM (Mục 1.2 & 2)
// ==========================================================================

function renderCatalog() {
  const items = appState.products || [];
  const grid = $("product-grid");

  $("result-count").textContent = `${appState.total} sản phẩm`;
  $("empty-state").classList.toggle("hidden", items.length > 0);
  $("pagination-wrap").classList.toggle("hidden", items.length === 0);

  // Sync category pills state
  document.querySelectorAll(".nav-item").forEach(b => {
    b.classList.toggle("active", b.dataset.cat === (appState.categoryTab || "all"));
  });
  document.querySelectorAll(".pill-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.catPill === (appState.categoryTab || "all"));
  });

  if (items.length === 0) {
    grid.innerHTML = "";
    return;
  }

  grid.innerHTML = items.map(p => {
    // Mục 1.2: Ưu tiên ảnh tối ưu image_web_url cho danh sách thẻ sản phẩm
    const primaryImg = p.images?.find(i => i.is_primary) || p.images?.[0];
    const cardImgUrl = resolveImageUrl(primaryImg?.image_web_url ?? primaryImg?.image_url);

    // Mục 2: Xử lý an toàn giá sản phẩm null
    const priceDisplay = formatProductPrice(p.price);

    const subName = p.category?.name || "";
    const colorHex = COLOR_HEX[(p.color || "").toLowerCase()] || "#94a3b8";

    // AI score badge nếu có
    const scoreBadge = typeof p.score === "number"
      ? `<div class="ai-score-badge"><svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg> Độ tương đồng: ${(p.score * 100).toFixed(1)}%</div>`
      : "";

    return `
      <article class="card">
        <div class="thumb" onclick="openDetailModal('${p.id}')">
          <img src="${cardImgUrl}" alt="${p.name}" loading="lazy" onerror="this.onerror=null; this.src='${CONFIG.PLACEHOLDER_IMAGE}';">
          
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
            <button class="card-action-btn" onclick="event.stopPropagation(); findSimilarProducts('${p.id}')">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
              </svg>
              Tìm tương tự
            </button>
          </div>
        </div>

        <div class="card-info">
          ${scoreBadge}
          <span class="card-label">${subName || "Thời trang nam"}</span>
          <h3 onclick="openDetailModal('${p.id}')">${p.name}</h3>

          <div class="dots" title="Màu: ${p.color || 'Đang cập nhật'}">
            <span class="dot" style="background:${colorHex}"></span>
            ${p.gender ? `<span style="font-size:0.75rem; color:var(--text-muted); margin-left:4px;">(${p.gender})</span>` : ""}
          </div>

          <div class="price-row">
            <span class="price">${priceDisplay}</span>
          </div>
        </div>
      </article>
    `;
  }).join("");
}

/**
 * Hiển thị kết quả tìm kiếm AI (Visual Search hoặc Multimodal Search) (Mục 3.3)
 */
function renderAiResults() {
  const items = appState.aiResults || [];
  const grid = $("product-grid");

  $("result-count").textContent = `${items.length} sản phẩm tương đồng (AI)`;
  $("empty-state").classList.toggle("hidden", items.length > 0);
  $("pagination-wrap").classList.add("hidden"); // AI search trả về top_k cố định

  if (items.length === 0) {
    grid.innerHTML = "";
    $("empty-title").textContent = "Không tìm thấy sản phẩm tương đồng";
    $("empty-desc").textContent = "Thử tải lên góc ảnh khác hoặc điều chỉnh mô tả phong cách.";
    return;
  }

  grid.innerHTML = items.map(item => {
    // Schema SearchResultItem: product_id, name, description, gender, color, price, category_name, primary_image_url, score
    const cardImgUrl = resolveImageUrl(item.primary_image_url);
    const priceDisplay = formatProductPrice(item.price);
    const scorePct = typeof item.score === "number" ? (item.score * 100).toFixed(1) : "0.0";
    const colorHex = COLOR_HEX[(item.color || "").toLowerCase()] || "#94a3b8";

    return `
      <article class="card">
        <div class="thumb" onclick="openDetailModal('${item.product_id}')">
          <img src="${cardImgUrl}" alt="${item.name}" loading="lazy" onerror="this.onerror=null; this.src='${CONFIG.PLACEHOLDER_IMAGE}';">

          <div class="card-actions-bar">
            <button class="card-action-btn" onclick="event.stopPropagation(); openDetailModal('${item.product_id}')">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"></circle>
                <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
              </svg>
              Xem chi tiết
            </button>
          </div>
        </div>

        <div class="card-info">
          <div class="ai-score-badge">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/>
            </svg>
            Độ tương đồng: ${scorePct}%
          </div>

          <span class="card-label">${item.category_name || "Thời trang nam"}</span>
          <h3 onclick="openDetailModal('${item.product_id}')">${item.name}</h3>

          <div class="dots" title="Màu: ${item.color || ''}">
            <span class="dot" style="background:${colorHex}"></span>
            ${item.gender ? `<span style="font-size:0.75rem; color:var(--text-muted); margin-left:4px;">(${item.gender})</span>` : ""}
          </div>

          <div class="price-row">
            <span class="price">${priceDisplay}</span>
          </div>
        </div>
      </article>
    `;
  }).join("");
}

// ==========================================================================
// 4. PHÂN TRANG PHÍA SERVER (Mục 4.1)
// ==========================================================================
function renderPagination() {
  const total = appState.total;
  const limit = appState.limit;
  const offset = appState.offset;

  if (total <= limit) {
    $("pagination-wrap").classList.add("hidden");
    return;
  }
  $("pagination-wrap").classList.remove("hidden");

  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil(total / limit);
  const startItem = offset + 1;
  const endItem = Math.min(offset + limit, total);

  $("pagination-info").innerHTML = `Hiển thị <strong>${startItem}</strong> – <strong>${endItem}</strong> trên <strong>${total}</strong> sản phẩm`;

  const ctrl = $("pagination-controls");
  let btns = [];

  // Nút Trang trước
  btns.push(`
    <button class="page-btn" ${currentPage === 1 ? 'disabled' : ''} onclick="goToPage(${currentPage - 1})" aria-label="Trang trước">
      &lsaquo;
    </button>
  `);

  // Sinh các nút số trang (tối đa 5 số)
  let startP = Math.max(1, currentPage - 2);
  let endP = Math.min(totalPages, startP + 4);
  if (endP - startP < 4) startP = Math.max(1, endP - 4);

  if (startP > 1) {
    btns.push(`<button class="page-btn" onclick="goToPage(1)">1</button>`);
    if (startP > 2) btns.push(`<span style="padding:0 4px; color:var(--text-muted);">…</span>`);
  }

  for (let p = startP; p <= endP; p++) {
    btns.push(`
      <button class="page-btn ${p === currentPage ? 'active' : ''}" onclick="goToPage(${p})">${p}</button>
    `);
  }

  if (endP < totalPages) {
    if (endP < totalPages - 1) btns.push(`<span style="padding:0 4px; color:var(--text-muted);">…</span>`);
    btns.push(`<button class="page-btn" onclick="goToPage(${totalPages})">${totalPages}</button>`);
  }

  // Nút Trang tiếp theo
  btns.push(`
    <button class="page-btn" ${currentPage === totalPages ? 'disabled' : ''} onclick="goToPage(${currentPage + 1})" aria-label="Trang sau">
      &rsaquo;
    </button>
  `);

  ctrl.innerHTML = btns.join("");
}

function goToPage(page) {
  appState.offset = (page - 1) * appState.limit;
  loadProducts();
  const catalogEl = document.querySelector(".catalog");
  if (catalogEl) {
    catalogEl.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

// ==========================================================================
// 5. BỘ LỌC, TÌM KIẾM TỪ KHÓA & SẮP XẾP (Mục 4.1 & 4.2)
// ==========================================================================

let searchDebounceTimeout = null;
function handleSearch(val) {
  clearTimeout(searchDebounceTimeout);
  searchDebounceTimeout = setTimeout(() => {
    appState.q = val || "";
    clearAiSearch(false);
    updateFilterIndicator();
    loadProducts(true);
  }, 350);
}

function filterCategory(tab) {
  appState.categoryTab = tab;
  clearAiSearch(false);

  if (tab === "all") {
    appState.categoryId = null;
  } else if (tab === "ao") {
    // Tìm UUID danh mục áo (Shoes vs Clothing hoặc T-Shirt, Jacket...)
    const found = appState.categories.find(c => /áo|shirt|hoodie|jacket|clothing|apparel/i.test(c.name));
    appState.categoryId = found ? found.id : null;
  } else if (tab === "giay") {
    // Tìm UUID danh mục giày (Shoes, Sneakers...)
    const found = appState.categories.find(c => /giày|giay|shoe|sneaker/i.test(c.name));
    appState.categoryId = found ? found.id : null;
  }

  updateFilterIndicator();
  loadProducts(true);
}

function onGenderFilterChange(gender) {
  appState.gender = gender;
  clearAiSearch(false);
  updateFilterIndicator();
  loadProducts(true);
}

function toggleColorFilter(color) {
  if (appState.color.toLowerCase() === color.toLowerCase()) {
    appState.color = "";
  } else {
    appState.color = color;
  }
  clearAiSearch(false);
  renderDynamicFacets(appState.filters);
  updateFilterIndicator();
  loadProducts(true);
}

function toggleColorsExpanded() {
  appState.colorsExpanded = !appState.colorsExpanded;
  if (appState.filters) {
    renderDynamicFacets(appState.filters);
  }
}


function onPriceSliderInput(val) {
  appState.maxPrice = parseInt(val, 10);
  appState.pricePreset = "custom";

  const display = $("price-max-display");
  if (display) display.textContent = formatProductPrice(appState.maxPrice);

  document.querySelectorAll(".price-preset-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.pricePreset === "custom");
  });

  clearAiSearch(false);
  loadProducts(true);
}

function setPricePreset(preset) {
  appState.pricePreset = preset;
  document.querySelectorAll(".price-preset-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.pricePreset === preset);
  });

  const slider = $("price-range-input");
  const display = $("price-max-display");

  if (preset === "all") {
    appState.minPrice = null;
    appState.maxPrice = null;
  } else if (preset === "under500") {
    appState.minPrice = null;
    appState.maxPrice = 500000;
  } else if (preset === "500-1500") {
    appState.minPrice = 500000;
    appState.maxPrice = 1500000;
  } else if (preset === "over1500") {
    appState.minPrice = 1500000;
    appState.maxPrice = null;
  }

  if (slider) {
    slider.value = appState.maxPrice != null ? appState.maxPrice : slider.max;
  }
  if (display) {
    display.textContent = appState.maxPrice != null ? formatProductPrice(appState.maxPrice) : "Tất cả";
  }

  clearAiSearch(false);
  loadProducts(true);
}

function sortCatalog(sortVal) {
  // Map value to backend sort param: "newest", "price_asc", "price_desc"
  if (sortVal === "price-asc") appState.sort = "price_asc";
  else if (sortVal === "price-desc") appState.sort = "price_desc";
  else appState.sort = "newest";

  loadProducts(true);
}

function updateFilterIndicator() {
  const ind = $("filter-indicator");
  const txt = $("filter-indicator-text");
  let parts = [];
  if (appState.q.trim()) parts.push(`Từ khóa: "${appState.q.trim()}"`);
  if (appState.categoryTab && appState.categoryTab !== "all") parts.push(`Nhóm: ${appState.categoryTab.toUpperCase()}`);
  if (appState.gender) parts.push(`Giới tính: ${appState.gender}`);
  if (appState.color) parts.push(`Màu: ${appState.color}`);
  if (appState.minPrice != null || appState.maxPrice != null) {
    parts.push(`Giá: ${formatProductPrice(appState.minPrice || 0)} - ${appState.maxPrice != null ? formatProductPrice(appState.maxPrice) : "Tất cả"}`);
  }

  if (parts.length > 0) {
    ind.classList.remove("hidden");
    txt.textContent = `Đang lọc theo: ${parts.join(" · ")}`;
  } else {
    ind.classList.add("hidden");
  }
}

function resetAll() {
  appState.q = "";
  appState.categoryId = null;
  appState.categoryTab = "all";
  appState.gender = "";
  appState.color = "";
  appState.minPrice = null;
  appState.maxPrice = null;
  appState.pricePreset = "all";
  appState.sort = "newest";
  appState.offset = 0;

  if ($("main-search-input")) $("main-search-input").value = "";
  if ($("sort-select")) $("sort-select").value = "default";
  if ($("gender-filter-select")) $("gender-filter-select").value = "";
  const slider = $("price-range-input");
  if (slider) slider.value = slider.max;
  if ($("price-max-display")) $("price-max-display").textContent = "Tất cả";

  document.querySelectorAll(".price-preset-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.pricePreset === "all");
  });

  clearAiSearch(false);
  renderDynamicFacets(appState.filters);
  updateFilterIndicator();
  loadProducts(true);
  showToast("Đã đặt lại toàn bộ bộ lọc sản phẩm.");
}

// ==========================================================================
// 6. TÍCH HỢP TÌM KIẾM AI: VISUAL SEARCH & MULTIMODAL SEARCH (Mục 3)
// ==========================================================================

function openImageSearchModal() {
  $("modal-image-search").classList.remove("hidden");
}

function closeImageSearchModal() {
  $("modal-image-search").classList.add("hidden");
}

function switchAiSearchMode(mode) {
  appState.aiSearchMode = mode;
  const isMulti = mode === "multimodal";
  $("ai-tab-visual").classList.toggle("active", !isMulti);
  $("ai-tab-multimodal").classList.toggle("active", isMulti);
  $("ai-multimodal-fields").classList.toggle("hidden", !isMulti);
  updateAiSubmitButtonState();
}

function onAiWeightChange(val) {
  appState.aiWeight = parseFloat(val);
  const imgPct = Math.round(appState.aiWeight * 100);
  const txtPct = 100 - imgPct;
  $("ai-weight-display").textContent = `${imgPct}% Ảnh — ${txtPct}% Văn bản`;
}

function setupImageDropzone() {
  const zone = $("clean-dropzone");
  if (!zone) return;

  ["dragenter", "dragover"].forEach(ev => {
    zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.add("over"); });
  });
  ["dragleave", "drop"].forEach(ev => {
    zone.addEventListener(ev, e => { e.preventDefault(); zone.classList.remove("over"); });
  });

  zone.addEventListener("drop", e => {
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleValidatedAiFile(e.dataTransfer.files[0]);
    }
  });
}

function handleAiFileSelected(e) {
  if (e.target.files && e.target.files[0]) {
    handleValidatedAiFile(e.target.files[0]);
  }
}

/**
 * Kiểm tra định dạng và kích thước file trước khi gửi request (Mục 3.3)
 */
function handleValidatedAiFile(file) {
  if (!CONFIG.ALLOWED_IMAGE_TYPES.includes(file.type)) {
    showToast("⚠️ Định dạng ảnh không hỗ trợ. Vui lòng chọn ảnh JPEG, PNG hoặc WEBP.");
    return;
  }
  if (file.size > CONFIG.MAX_UPLOAD_BYTES) {
    showToast("⚠️ Kích thước ảnh vượt quá giới hạn 10MB.");
    return;
  }

  appState.aiSelectedFile = file;

  // Hiển thị preview
  const reader = new FileReader();
  reader.onload = ev => {
    $("ai-preview-img").src = ev.target.result;
    $("ai-preview-box").classList.remove("hidden");
    $("clean-dropzone").classList.add("hidden");
  };
  reader.readAsDataURL(file);

  updateAiSubmitButtonState();
}

function removeAiSelectedImage() {
  appState.aiSelectedFile = null;
  $("ai-file-input").value = "";
  $("ai-preview-box").classList.add("hidden");
  $("clean-dropzone").classList.remove("hidden");
  updateAiSubmitButtonState();
}

function updateAiSubmitButtonState() {
  const btn = $("ai-submit-search-btn");
  if (!btn) return;
  const hasFile = !!appState.aiSelectedFile;
  btn.disabled = !hasFile;
}

/**
 * Thực thi gọi API tìm kiếm AI thực tế lên Backend FastAPI (Mục 3.1 & 3.2)
 */
async function executeAiSearch() {
  if (!appState.aiSelectedFile) return;

  const btn = $("ai-submit-search-btn");
  const btnText = $("ai-submit-text");
  btn.disabled = true;
  btnText.innerHTML = `<span class="spinner" style="margin-right:8px; vertical-align:middle;"></span> AI SigLIP đang tìm kiếm...`;

  const formData = new FormData();
  formData.append("image", appState.aiSelectedFile);

  try {
    let url = "";
    if (appState.aiSearchMode === "multimodal") {
      // Mục 3.2: POST /api/v1/search/multimodal?top_k=10&image_weight=0.5
      const textQuery = ($("ai-text-query").value || "").trim();
      if (!textQuery) {
        showToast("⚠️ Vui lòng nhập mô tả phong cách cho tìm kiếm đa phương thức.");
        btn.disabled = false;
        btnText.textContent = "Bắt đầu tìm kiếm AI";
        return;
      }
      formData.append("text_query", textQuery);
      url = `${CONFIG.API_V1_URL}/search/multimodal?top_k=12&image_weight=${appState.aiWeight}`;
    } else {
      // Mục 3.1: POST /api/v1/search/image?top_k=10
      url = `${CONFIG.API_V1_URL}/search/image?top_k=12`;
    }

    const response = await fetch(url, {
      method: "POST",
      body: formData // Không tự đặt header Content-Type multipart/form-data
    });

    if (!response.ok) {
      const errJson = await response.json().catch(() => null);
      throw new Error(errJson?.detail || `Lỗi AI Search: ${response.status}`);
    }

    const data = await response.json();
    appState.aiResults = data.results || [];
    appState.activeMode = "ai";
    appState.aiMeta = {
      type: appState.aiSearchMode,
      query: appState.aiSearchMode === "multimodal" ? $("ai-text-query").value : "",
      weight: appState.aiWeight,
      total: appState.aiResults.length
    };

    closeImageSearchModal();

    // Hiển thị Banner trạng thái AI đang kích hoạt
    const banner = $("ai-active-banner");
    const bannerBadge = $("ai-banner-badge");
    const bannerText = $("ai-banner-text");

    if (banner) {
      banner.classList.remove("hidden");
      bannerBadge.textContent = appState.aiSearchMode === "multimodal" ? "Multimodal AI" : "Visual AI";
      bannerText.innerHTML = appState.aiSearchMode === "multimodal"
        ? `Kết quả cho ảnh kèm mô tả: <strong>"${appState.aiMeta.query}"</strong> (${appState.aiResults.length} sản phẩm tương đồng)`
        : `Tìm thấy <strong>${appState.aiResults.length} sản phẩm tương đồng</strong> qua vector đặc trưng ảnh`;
    }

    renderAiResults();
    showToast(`Đã tìm thấy ${appState.aiResults.length} sản phẩm tương đồng cao nhất.`);

    const catalogEl = document.querySelector(".catalog");
    if (catalogEl) catalogEl.scrollIntoView({ behavior: "smooth", block: "start" });

  } catch (err) {
    console.error("Lỗi AI Search:", err);
    showToast(`Không thể tìm kiếm sản phẩm phù hợp: ${err.message}`);
  } finally {
    btn.disabled = false;
    btnText.textContent = "Bắt đầu tìm kiếm bằng hình ảnh";
  }
}

function clearAiSearch(reFetch = true) {
  appState.activeMode = "catalog";
  appState.aiResults = [];
  appState.aiMeta = null;
  const banner = $("ai-active-banner");
  if (banner) banner.classList.add("hidden");

  if (reFetch) {
    loadProducts(true);
    showToast("Đã quay lại danh mục sản phẩm chuẩn.");
  }
}

/**
 * Thử ảnh mẫu catalog: Tải ảnh về dạng blob và gửi API thật
 */
async function simulatePresetSearch(cat) {
  closeImageSearchModal();
  showToast("Đang tải ảnh mẫu và tìm kiếm sản phẩm...");

  const presetUrls = {
    ao: "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?auto=format&fit=crop&w=600&q=80",
    quan: "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?auto=format&fit=crop&w=600&q=80",
    giay: "https://images.unsplash.com/photo-1549298916-b41d501d3772?auto=format&fit=crop&w=600&q=80"
  };

  try {
    const res = await fetch(presetUrls[cat]);
    const blob = await res.blob();
    const file = new File([blob], `${cat}_sample.jpg`, { type: "image/jpeg" });
    appState.aiSelectedFile = file;
    appState.aiSearchMode = "visual";
    executeAiSearch();
  } catch (err) {
    // Fallback nếu không kết nối được Unsplash
    filterCategory(cat);
  }
}

function findSimilarProducts(productId) {
  const p = appState.products.find(x => x.id === productId);
  if (!p) return;
  const primaryImg = p.images?.find(i => i.is_primary) || p.images?.[0];
  const url = resolveImageUrl(primaryImg?.image_url);

  showToast(`Đang trích xuất đặc trưng cho: ${p.name}...`);
  fetch(url)
    .then(r => r.blob())
    .then(blob => {
      const file = new File([blob], `${p.id}.jpg`, { type: "image/jpeg" });
      appState.aiSelectedFile = file;
      appState.aiSearchMode = "visual";
      executeAiSearch();
    })
    .catch(() => {
      filterCategory(p.category?.name?.toLowerCase().includes("giày") ? "giay" : "ao");
    });
}

// ==========================================================================
// 7. XÁC THỰC NGƯỜI DÙNG: ĐĂNG NHẬP & ĐĂNG KÝ (Mục 5)
// ==========================================================================

function openAuthModal(defaultTab = "login") {
  switchAuthTab(defaultTab);
  $("modal-auth").classList.remove("hidden");
  $("auth-alert-error").classList.add("hidden");
}

function closeAuthModal() {
  $("modal-auth").classList.add("hidden");
}

function switchAuthTab(tab) {
  const isLogin = tab === "login";
  $("auth-tab-login").classList.toggle("active", isLogin);
  $("auth-tab-register").classList.toggle("active", !isLogin);
  $("login-form").classList.toggle("hidden", !isLogin);
  $("register-form").classList.toggle("hidden", isLogin);
  $("auth-alert-error").classList.add("hidden");
  $("auth-modal-title").textContent = isLogin ? "Đăng nhập EAST & SOUL" : "Đăng ký thành viên mới";
}

function toggleUserDropdown() {
  if (!appState.currentUser) {
    openAuthModal("login");
  } else {
    $("user-dropdown-menu").classList.toggle("hidden");
  }
}

/**
 * Khôi phục phiên đăng nhập khi tải lại trang qua GET /api/v1/auth/me (Mục 5)
 */
async function checkAuthSession() {
  if (!appState.token) {
    updateUserAuthUI(null);
    return;
  }

  try {
    const res = await fetch(`${CONFIG.API_V1_URL}/auth/me`, {
      headers: {
        "Authorization": `Bearer ${appState.token}`
      }
    });

    if (res.ok) {
      const user = await res.json();
      appState.currentUser = user;
      updateUserAuthUI(user);
    } else {
      // Token hết hạn
      handleLogout(false);
    }
  } catch (err) {
    console.warn("Chưa thể xác thực phiên người dùng:", err.message);
  }
}

/**
 * Xử lý đăng nhập POST /api/v1/auth/login (Mục 5)
 */
async function handleLoginSubmit(e) {
  e.preventDefault();
  const email = $("login-email").value.trim();
  const password = $("login-password").value;
  const btn = $("login-submit-btn");
  const errBox = $("auth-alert-error");

  btn.disabled = true;
  btn.innerHTML = `<span class="spinner" style="margin-right:6px;"></span> Đang đăng nhập...`;
  errBox.classList.add("hidden");

  try {
    const res = await fetch(`${CONFIG.API_V1_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Đăng nhập thất bại");

    // Lưu token theo cơ chế đã thống nhất (localStorage)
    appState.token = data.access_token;
    appState.currentUser = data.user;
    localStorage.setItem("es_auth_token", data.access_token);

    updateUserAuthUI(data.user);
    closeAuthModal();
    showToast(`👋 Chào mừng trở lại, ${data.user.name}!`);
  } catch (err) {
    errBox.textContent = err.message;
    errBox.classList.remove("hidden");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>Đăng nhập</span>`;
  }
}

/**
 * Xử lý đăng ký POST /api/v1/auth/register (Mục 5)
 * Response trả về access token và thông tin người dùng, lưu phiên ngay không bắt đăng nhập lại.
 */
async function handleRegisterSubmit(e) {
  e.preventDefault();
  const name = $("reg-name").value.trim();
  const email = $("reg-email").value.trim();
  const password = $("reg-password").value;
  const btn = $("reg-submit-btn");
  const errBox = $("auth-alert-error");

  btn.disabled = true;
  btn.innerHTML = `<span class="spinner" style="margin-right:6px;"></span> Đang tạo tài khoản...`;
  errBox.classList.add("hidden");

  try {
    const res = await fetch(`${CONFIG.API_V1_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, password })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Đăng ký không thành công");

    // Lưu phiên ngay sau khi đăng ký thành công
    appState.token = data.access_token;
    appState.currentUser = data.user;
    localStorage.setItem("es_auth_token", data.access_token);

    updateUserAuthUI(data.user);
    closeAuthModal();
    showToast(`🎉 Tạo tài khoản thành công! Chào mừng ${data.user.name}.`);
  } catch (err) {
    errBox.textContent = err.message;
    errBox.classList.remove("hidden");
  } finally {
    btn.disabled = false;
    btn.innerHTML = `<span>Tạo tài khoản &amp; Đăng nhập</span>`;
  }
}

function handleLogout(showNotification = true) {
  appState.token = null;
  appState.currentUser = null;
  localStorage.removeItem("es_auth_token");
  updateUserAuthUI(null);
  $("user-dropdown-menu").classList.add("hidden");
  if (showNotification) showToast("Đã đăng xuất tài khoản.");
}

function updateUserAuthUI(user) {
  const btnLabel = $("user-btn-label");
  const avatarBadge = $("user-avatar-badge");

  if (user) {
    btnLabel.textContent = user.name.split(" ").pop() || user.name;
    avatarBadge.textContent = (user.name[0] || "U").toUpperCase();
    $("user-dropdown-name").textContent = user.name;
    $("user-dropdown-email").textContent = user.email;
    $("user-dropdown-role").textContent = user.role || "USER";
  } else {
    btnLabel.textContent = "Đăng nhập";
    avatarBadge.innerHTML = `
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
      </svg>
    `;
    $("user-dropdown-name").textContent = "Khách";
    $("user-dropdown-email").textContent = "Chưa đăng nhập";
    $("user-dropdown-role").textContent = "GUEST";
  }
}

// ==========================================================================
// 8. MODAL CHI TIẾT SẢN PHẨM & MÃ QR (Mục 1.2 & 2)
// ==========================================================================

async function openDetailModal(id) {
  // Tìm trong appState hoặc gọi GET /api/v1/products/{id}
  let p = appState.products.find(x => x.id === id);
  if (!p && appState.aiResults) {
    p = appState.aiResults.find(x => x.product_id === id);
  }

  // Luôn fetch chi tiết đầy đủ từ GET /api/v1/products/{id} để có ảnh gốc độ phân giải cao
  try {
    const res = await fetch(`${CONFIG.API_V1_URL}/products/${id}`);
    if (res.ok) {
      p = await res.json();
    }
  } catch (err) {
    console.warn("Không tải được chi tiết API, dùng dữ liệu cache:", err);
  }

  if (!p) return;

  // Mục 1.2: Trang chi tiết dùng ảnh gốc độ phân giải cao (image_url)
  const primaryImg = p.images?.find(i => i.is_primary) || p.images?.[0];
  const detailImgUrl = resolveImageUrl(primaryImg?.image_url || p.primary_image_url);

  // Mục 2: Giá có thể null
  const priceDisplay = formatProductPrice(p.price);
  const qrSvg = generateCleanQrSvg(p.id.slice(0, 8).toUpperCase());

  $("detail-body").innerHTML = `
    <div class="detail-grid">
      <div class="detail-media">
        <img class="detail-main-img" src="${detailImgUrl}" alt="${p.name}" onerror="this.onerror=null; this.src='${CONFIG.PLACEHOLDER_IMAGE}';">
      </div>

      <div class="detail-content">
        <span class="detail-category">${p.category?.name || p.category_name || "Thời trang nam"} · Mã: SP-${p.id.slice(0, 8).toUpperCase()}</span>
        <h2 class="detail-title">${p.name}</h2>

        <div class="detail-rating">
          <span class="stars">★★★★★</span>
          <strong>4.8</strong>
          <span>(Đánh giá trải nghiệm thực tế)</span>
        </div>

        <div class="detail-price-box">
          <span class="detail-price">${priceDisplay}</span>
        </div>

        <p class="detail-desc">${p.description || "Chưa có mô tả chi tiết cho sản phẩm này."}</p>

        <!-- Kích thước -->
        <div class="option-label">
          <span>Kích thước:</span>
          <a href="#" onclick="showToast('Bảng size chuẩn Regular fit Việt Nam'); return false;" style="font-size:0.75rem; text-decoration:underline; color:var(--text-muted);">Bảng quy đổi</a>
        </div>
        <div class="size-selector">
          <button class="size-btn" onclick="selectDetailSize(this)">S</button>
          <button class="size-btn active" onclick="selectDetailSize(this)">M</button>
          <button class="size-btn" onclick="selectDetailSize(this)">L</button>
          <button class="size-btn" onclick="selectDetailSize(this)">XL</button>
        </div>

        <!-- Màu sắc -->
        <div class="option-label">
          <span>Màu sắc: <strong>${p.color || "Tiêu chuẩn"}</strong></span>
        </div>
        <div class="color-selector">
          <span class="color-option active" style="background:${COLOR_HEX[(p.color || '').toLowerCase()] || '#94a3b8'}" title="${p.color || 'Mặc định'}"></span>
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
          <button class="btn btn-ghost btn-block" onclick="findSimilarProducts('${p.id}'); closeDetailModal();">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            </svg>
            Xem sản phẩm tương tự (AI SigLIP)
          </button>
        </div>

        <!-- Thẻ mã QR sản phẩm -->
        <div class="product-qr-card">
          <div class="product-qr-svg-wrap">
            ${qrSvg}
          </div>
          <div class="product-qr-info">
            <span class="product-qr-title">Mã QR sản phẩm: SP-${p.id.slice(0, 8).toUpperCase()}</span>
            <span class="product-qr-sub">Quét mã QR tại cửa hàng để mở nhanh trang chi tiết này.</span>
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

function openProductQr(id) {
  openDetailModal(id);
  setTimeout(() => {
    const el = document.querySelector(".product-qr-card");
    if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
  }, 250);
}

// ==========================================================================
// 9. GIỎ HÀNG & THANH TOÁN (Mục 2: Xử lý an toàn giá null)
// ==========================================================================

function toggleCartDrawer() {
  $("cart-drawer").classList.toggle("open");
  $("cart-backdrop").classList.toggle("hidden");
  renderCart();
}

function addToCart(id) {
  let product = appState.products.find(p => p.id === id);
  if (!product && appState.aiResults) {
    const aiItem = appState.aiResults.find(p => p.product_id === id);
    if (aiItem) {
      product = {
        id: aiItem.product_id,
        name: aiItem.name,
        price: aiItem.price,
        images: [{ image_web_url: aiItem.primary_image_url, image_url: aiItem.primary_image_url }]
      };
    }
  }
  if (!product) return;

  const existing = appState.cart.find(c => c.product.id === id);
  if (existing) {
    existing.qty++;
  } else {
    appState.cart.push({ product, qty: 1 });
  }
  updateCartBadge();
  showToast(`Đã thêm "${product.name}" vào giỏ hàng.`);
}

function updateCartQty(id, delta) {
  const item = appState.cart.find(c => c.product.id === id);
  if (!item) return;
  item.qty += delta;
  if (item.qty <= 0) {
    appState.cart = appState.cart.filter(c => c.product.id !== id);
  }
  updateCartBadge();
  renderCart();
}

function removeFromCart(id) {
  appState.cart = appState.cart.filter(c => c.product.id !== id);
  updateCartBadge();
  renderCart();
  showToast("Đã xóa sản phẩm khỏi giỏ.");
}

function updateCartBadge() {
  const totalCount = appState.cart.reduce((s, c) => s + c.qty, 0);
  $("cart-counter").textContent = totalCount;
  $("cart-count-sub").textContent = `${totalCount} món đồ`;
}

function renderCart() {
  const list = $("cart-items-list");
  // Mục 2: Nếu giá null hoặc undefined thì tính là 0
  const subtotal = appState.cart.reduce((s, c) => {
    const priceNum = c.product.price != null ? Number(c.product.price) : 0;
    return s + priceNum * c.qty;
  }, 0);

  // Thanh tiến độ Freeship
  const fillPct = Math.min(100, Math.round((subtotal / FREESHIP_THRESHOLD) * 100));
  $("shipping-progress-fill").style.width = `${fillPct}%`;
  if (subtotal >= FREESHIP_THRESHOLD) {
    $("shipping-progress-text").innerHTML = `🎉 Bạn đã đủ điều kiện <strong>Miễn phí vận chuyển</strong>!`;
  } else {
    const diff = FREESHIP_THRESHOLD - subtotal;
    $("shipping-progress-text").textContent = `Thêm ${formatProductPrice(diff)} để được Freeship toàn quốc!`;
  }

  if (!appState.cart.length) {
    list.innerHTML = `
      <div style="text-align:center; padding: 48px 0; color: var(--text-muted);">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom:12px; color:var(--text-subtle);">
          <path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <path d="M16 10a4 4 0 0 1-8 0"></path>
        </svg>
        <p style="font-weight:600; color:var(--ink);">Giỏ hàng đang trống</p>
        <p style="font-size:0.85rem; margin-top:4px;">Khám phá bộ sưu tập và chọn sản phẩm ưng ý.</p>
      </div>
    `;
    $("cart-subtotal-price").textContent = "0 đ";
    $("cart-discount-row").classList.add("hidden");
    $("cart-total-price").textContent = "0 đ";
    return;
  }

  list.innerHTML = appState.cart.map(c => {
    const primaryImg = c.product.images?.find(i => i.is_primary) || c.product.images?.[0];
    const imgUrl = resolveImageUrl(primaryImg?.image_web_url ?? primaryImg?.image_url);
    const priceText = formatProductPrice(c.product.price);

    return `
      <div class="cart-item">
        <img src="${imgUrl}" alt="${c.product.name}" onerror="this.onerror=null; this.src='${CONFIG.PLACEHOLDER_IMAGE}';">
        <div class="cart-item-details">
          <div class="cart-item-title">${c.product.name}</div>
          <div class="cart-item-price">${priceText}</div>
          
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
    `;
  }).join("");

  $("cart-subtotal-price").textContent = formatProductPrice(subtotal);

  // Voucher
  let discount = 0;
  if (appState.appliedVoucher) {
    discount = Math.round((subtotal * appState.appliedVoucher.discountPercent) / 100);
    $("cart-discount-row").classList.remove("hidden");
    $("cart-discount-price").textContent = `-${formatProductPrice(discount)}`;
  } else {
    $("cart-discount-row").classList.add("hidden");
  }

  const finalTotal = Math.max(0, subtotal - discount);
  $("cart-total-price").textContent = formatProductPrice(finalTotal);
}

function applyPromoCode() {
  const input = $("promo-input");
  const code = (input.value || "").trim().toUpperCase();
  if (code === "SOUL20") {
    appState.appliedVoucher = { code: "SOUL20", discountPercent: 20 };
    $("promo-applied-tag").classList.remove("hidden");
    input.value = "";
    renderCart();
    showToast("Đã áp dụng mã SOUL20: Giảm 20% đơn hàng!");
  } else if (!code) {
    showToast("Vui lòng nhập mã giảm giá.");
  } else {
    showToast(`Mã "${code}" không hợp lệ hoặc đã hết hạn.`);
  }
}

function removePromoCode() {
  appState.appliedVoucher = null;
  $("promo-applied-tag").classList.add("hidden");
  renderCart();
  showToast("Đã gỡ bỏ mã giảm giá.");
}

function handleCheckout() {
  if (!appState.cart.length) {
    showToast("Giỏ hàng đang trống. Vui lòng chọn sản phẩm.");
    return;
  }
  const total = $("cart-total-price").textContent;
  appState.cart = [];
  appState.appliedVoucher = null;
  $("promo-applied-tag").classList.add("hidden");
  updateCartBadge();
  renderCart();
  toggleCartDrawer();
  showToast(`🎉 Đặt hàng thành công (${total})! EAST & SOUL sẽ liên hệ giao hàng trong 2h.`);
}

// ==========================================================================
// 10. CHỤP ẢNH TỪ ĐIỆN THOẠI & QUÉT QR CODE
// ==========================================================================

let phoneSessionId = null;
let phonePollInterval = null;
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

  const tabPhone = $("qr-tab-phone");
  const tabUpload = $("qr-tab-upload");
  if (tabPhone) tabPhone.classList.toggle("active", isPhone);
  if (tabUpload) tabUpload.classList.toggle("active", isUpload);

  const phoneView = $("qr-phone-view");
  const uploadView = $("qr-upload-view");
  if (phoneView) phoneView.classList.toggle("hidden", !isPhone);
  if (uploadView) uploadView.classList.toggle("hidden", !isUpload);

  if (isPhone) startPhoneSession();
  else stopPhoneSession();
}

function getLanIp() {
  const saved = localStorage.getItem("es_wifi_lan_ip");
  if (saved && saved.trim()) return saved.trim();
  const cur = window.location.hostname;
  if (cur && cur !== "localhost" && cur !== "127.0.0.1") return cur;
  return "192.168.2.26"; // IP Wi-Fi máy tính hiện tại
}

function updateLanIp(val) {
  if (!val || !val.trim()) return;
  const clean = val.trim();
  localStorage.setItem("es_wifi_lan_ip", clean);
  showToast(`Đã lưu IP Wi-Fi: ${clean}`);
  startPhoneSession();
}

function copyMobileUrl() {
  const lanIp = getLanIp();
  const port = window.location.port ? `:${window.location.port}` : ":3000";
  const path = window.location.pathname.replace("index.html", "");
  const url = `http://${lanIp}${port}${path}mobile-camera.html?session=${phoneSessionId}&v=2`;

  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(url).then(() => {
      showToast("📋 Đã sao chép link camera! Bạn có thể dán vào Zalo/trình duyệt.");
    }).catch(() => {
      prompt("Sao chép link này và dán vào trình duyệt điện thoại:", url);
    });
  } else {
    prompt("Sao chép link này và dán vào trình duyệt điện thoại:", url);
  }
}


function startPhoneSession() {
  stopPhoneSession();
  phoneSessionId = Math.random().toString(36).slice(2, 10).toUpperCase();

  const idEl = $("session-id-display");
  if (idEl) idEl.textContent = `Session: ${phoneSessionId}`;

  const lanIp = getLanIp();
  const ipInput = $("wifi-ip-input");
  if (ipInput) ipInput.value = lanIp;

  // Xây dựng URL ngắn gọn để mã QR to, rõ, điện thoại quét bắt nét cực nhanh
  const port = window.location.port ? `:${window.location.port}` : ":3000";
  const mobileHost = `http://${lanIp}${port}`;
  const path = window.location.pathname.replace("index.html", "");
  const mobileUrl = `${mobileHost}${path}mobile-camera.html?session=${phoneSessionId}&v=2`;


  const previewEl = $("mobile-url-preview");
  if (previewEl) previewEl.textContent = mobileUrl;

  const renderEl = $("session-qr-render");
  if (renderEl) {
    renderEl.innerHTML = "";
    if (window.QRCode) {
      new QRCode(renderEl, {
        text: mobileUrl,
        width: 140,
        height: 140,
        colorDark: "#000000",
        colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.L
      });
    } else {
      renderEl.innerHTML = generateCleanQrSvg(mobileUrl);
    }
  }


  const waiting = $("qr-phone-waiting");
  const received = $("qr-phone-received");
  if (waiting) waiting.classList.remove("hidden");
  if (received) received.classList.add("hidden");

  // Đăng ký session trên backend relay
  fetch(`${CONFIG.API_V1_URL}/camera/session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: phoneSessionId })
  }).catch(() => { });

  listenForPhonePhoto();
}

function stopPhoneSession() {
  if (phonePollInterval) { clearInterval(phonePollInterval); phonePollInterval = null; }
  if (broadcastChannel) { try { broadcastChannel.close(); } catch (e) { } broadcastChannel = null; }
}

function listenForPhonePhoto() {
  if (window.BroadcastChannel) {
    try {
      broadcastChannel = new BroadcastChannel("es_camera_sync");
      broadcastChannel.onmessage = ev => {
        if (ev.data && ev.data.sessionId === phoneSessionId && ev.data.image) {
          onPhotoReceived(ev.data);
        }
      };
    } catch (e) { }
  }

  phonePollInterval = setInterval(async () => {
    // 1. Kiểm tra Backend Relay (hoạt động đa thiết bị qua mạng LAN Wi-Fi)
    try {
      const res = await fetch(`${CONFIG.API_V1_URL}/camera/status/${phoneSessionId}?consume=true`);
      if (res.ok) {
        const data = await res.json();
        if (data.status === "ready" && data.image) {
          onPhotoReceived(data);
          return;
        }
      }
    } catch (err) { }

    // 2. Kiểm tra LocalStorage dự phòng (cho test cùng máy tính)
    try {
      const raw = localStorage.getItem("es_mobile_latest_event");
      if (raw) {
        const ev = JSON.parse(raw);
        if (ev.sessionId === phoneSessionId && ev.image) {
          onPhotoReceived(ev);
        }
      }
    } catch (e) { }
  }, 1000);
}


function onPhotoReceived(data) {
  stopPhoneSession();
  const waiting = $("qr-phone-waiting");
  const received = $("qr-phone-received");
  if (waiting) waiting.classList.add("hidden");
  if (received) received.classList.remove("hidden");

  const preview = $("received-phone-img") || $("qr-phone-photo-preview");
  if (preview) {
    preview.src = data.image;
    preview.style.display = "block";
  }


  appState.phoneCapturedDataUrl = data.image;
  showToast("Đã nhận ảnh từ điện thoại!");
}

function applyPhotoSearch() {
  closeQrScanModal();
  if (!appState.phoneCapturedDataUrl) return;

  // Chuyển DataURL thành Blob File để gọi endpoint AI Search thật
  fetch(appState.phoneCapturedDataUrl)
    .then(res => res.blob())
    .then(blob => {
      const file = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
      appState.aiSelectedFile = file;
      appState.aiSearchMode = "visual";
      executeAiSearch();
    })
    .catch(() => {
      filterCategory("ao");
    });
}

function resetPhoneSession() {
  startPhoneSession();
}

function openMobileCameraLocal() {
  const url = `mobile-camera.html?session=${phoneSessionId}`;
  window.open(url, "_blank", "width=420,height=750");
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
    if (ev.dataTransfer.files[0]) handleQrFileUpload(ev.dataTransfer.files[0]);
  });
}

function handleQrFileSelected(e) {
  if (e.target.files[0]) handleQrFileUpload(e.target.files[0]);
}

function handleQrFileUpload(file) {
  closeQrScanModal();
  handleValidatedAiFile(file);
  executeAiSearch();
}

function simulateQrScan(code) {
  closeQrScanModal();
  if (code.includes("SOUL20")) {
    appState.appliedVoucher = { code: "SOUL20", discountPercent: 20 };
    $("promo-applied-tag").classList.remove("hidden");
    renderCart();
    toggleCartDrawer();
    showToast("🎉 Quét QR thành công! Đã áp dụng Voucher giảm 20% (SOUL20).");
  } else {
    showToast(`🔍 Quét mã: ${code}`);
    handleSearch(code);
  }
}

// Bộ tạo SVG mã QR nội bộ
function generateCleanQrSvg(code) {
  const seed = (code || "").split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);
  const size = 21;
  let rects = "";

  const drawCorner = (ox, oy) => {
    rects += `<rect x="${ox}" y="${oy}" width="7" height="7" fill="#0f172a" rx="1.2"/>`;
    rects += `<rect x="${ox + 1}" y="${oy + 1}" width="5" height="5" fill="#ffffff" rx="0.8"/>`;
    rects += `<rect x="${ox + 2}" y="${oy + 2}" width="3" height="3" fill="#0f172a" rx="0.5"/>`;
  };
  drawCorner(0, 0);
  drawCorner(14, 0);
  drawCorner(0, 14);

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      if ((x < 8 && y < 8) || (x > 13 && y < 8) || (x < 8 && y > 13)) continue;
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
// 11. THÔNG BÁO TOAST
// ==========================================================================
function showToast(msg) {
  const box = $("toast-box");
  if (!box) return;
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