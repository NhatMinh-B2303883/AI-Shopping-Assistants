/**
 * EAST & SOUL — Modern Minimalist Shopping Assistant
 * Hỗ trợ tìm kiếm đa phương thức: Từ khóa, Ảnh AI, Quét mã QR
 */

// ── Dữ liệu 12 sản phẩm danh mục ──
const PRODUCTS = [
  {
    id: "ao-1",
    code: "PROD-ao-1",
    category: "ao",
    label: "Áo polo",
    name: "Áo polo Excool thoáng khí",
    price: 299000,
    oldPrice: 350000,
    tag: "Bán chạy",
    colors: ["#2d3748", "#1a202c", "#ffffff"],
    colorNames: ["Xanh đen", "Đen tuyền", "Trắng"],
    image: "1618354691373-d851c5c3a990",
    description: "Sợi Excool siêu nhẹ, thoát ẩm tức thì, co giãn 4 chiều cho ngày dài hoạt động năng động.",
    rating: 4.9,
    reviews: 142
  },
  {
    id: "ao-2",
    code: "PROD-ao-2",
    category: "ao",
    label: "Áo thun",
    name: "Áo thun cotton compact chống co rút",
    price: 199000,
    oldPrice: 249000,
    tag: "Mới",
    colors: ["#ffffff", "#64748b", "#0f172a"],
    colorNames: ["Trắng tinh", "Xám ghi", "Xanh navy"],
    image: "1521572267360-ee0c2909d518",
    description: "Cotton chải kỹ 220gsm dày dặn đứng form, công nghệ wash mềm chống xù lông tuyệt đối.",
    rating: 4.8,
    reviews: 86
  },
  {
    id: "ao-3",
    code: "PROD-ao-3",
    category: "ao",
    label: "Áo hoodie",
    name: "Áo hoodie nỉ bông giữ nhiệt",
    price: 590000,
    oldPrice: 690000,
    tag: "Thu đông",
    colors: ["#9ca3af", "#111827", "#1e3a8a"],
    colorNames: ["Xám tiêu", "Đen", "Xanh chàm"],
    image: "1556905055-8f358a7a47b2",
    description: "Nỉ bông 360gsm cào mịn bên trong, mũ hai lớp đứng form, túi kangaroo rộng rãi tiện ích.",
    rating: 4.9,
    reviews: 210
  },
  {
    id: "ao-4",
    code: "PROD-ao-4",
    category: "ao",
    label: "Áo sơ mi",
    name: "Áo sơ mi dài tay chống nhăn",
    price: 399000,
    oldPrice: 480000,
    tag: "",
    colors: ["#ffffff", "#93c5fd", "#1f2937"],
    colorNames: ["Trắng", "Xanh phấn", "Xám than"],
    image: "1602810318383-e386cc2a3ccf",
    description: "Chất liệu sợi tre Bamboo pha spandex tự nhiên, thoáng mát, giữ form phẳng phiu cả ngày.",
    rating: 4.7,
    reviews: 54
  },
  {
    id: "quan-1",
    code: "PROD-quan-1",
    category: "quan",
    label: "Quần dài",
    name: "Quần dài co giãn 4 chiều Daily Pants",
    price: 449000,
    oldPrice: 520000,
    tag: "Hot",
    colors: ["#1f2937", "#374151", "#78716c"],
    colorNames: ["Đen nhám", "Xám đậm", "Kaki sáng"],
    image: "1624378439575-d8705ad7ae80",
    description: "Phom suông hiện đại tôn dáng, cạp chun ẩn co giãn linh hoạt, thanh lịch cả đi làm lẫn đi chơi.",
    rating: 4.9,
    reviews: 175
  },
  {
    id: "quan-2",
    code: "PROD-quan-2",
    category: "quan",
    label: "Quần jeans",
    name: "Quần jeans slim-fit xanh chàm",
    price: 550000,
    oldPrice: 650000,
    tag: "Bán chạy",
    colors: ["#1e3a8a", "#0f172a"],
    colorNames: ["Xanh chàm wash", "Đen chàm"],
    image: "1541099649105-f69ad21f3246",
    description: "Denim 12oz dệt chéo bền bỉ pha 2% spandex, wash enzyme tự nhiên bền màu sau nhiều lần giặt.",
    rating: 4.8,
    reviews: 120
  },
  {
    id: "quan-3",
    code: "PROD-quan-3",
    category: "quan",
    label: "Quần short",
    name: "Quần short thể thao hai lớp Running",
    price: 249000,
    oldPrice: 299000,
    tag: "Xuân hè",
    colors: ["#111827", "#1e3a8a", "#059669"],
    colorNames: ["Đen", "Xanh navy", "Xanh lục"],
    image: "1591195853828-11db59a44f6b",
    description: "Lớp lót co giãn ôm sát cơ bắp, túi sau có khóa zip bảo vệ điện thoại khi chạy bộ.",
    rating: 4.7,
    reviews: 93
  },
  {
    id: "quan-4",
    code: "PROD-quan-4",
    category: "quan",
    label: "Quần jogger",
    name: "Quần jogger nỉ thu đông Minimalist",
    price: 420000,
    oldPrice: 490000,
    tag: "Thu đông",
    colors: ["#374151", "#111827"],
    colorNames: ["Ghi xám", "Đen tuyền"],
    image: "1506629082955-511b1aa562c8",
    description: "Bo gấu thun co giãn nhẹ, vải nỉ da cá êm mềm, giữ nhiệt ấm áp trong những ngày se lạnh.",
    rating: 4.8,
    reviews: 64
  },
  {
    id: "giay-1",
    code: "PROD-giay-1",
    category: "giay",
    label: "Sneaker",
    name: "Giày sneaker da trắng tối giản Clean Court",
    price: 890000,
    oldPrice: 1100000,
    tag: "Hot",
    colors: ["#ffffff", "#f3f4f6"],
    colorNames: ["Trắng viền kem", "Trắng tinh"],
    image: "1549298916-b41d501d3772",
    description: "Chất liệu da Nappa mềm cao cấp, lót trong êm ái, đế cao su khâu viền chắc chắn chống trượt.",
    rating: 5.0,
    reviews: 312
  },
  {
    id: "giay-2",
    code: "PROD-giay-2",
    category: "giay",
    label: "Sneaker",
    name: "Sneaker cổ thấp phong cách Retro 90s",
    price: 950000,
    oldPrice: 1200000,
    tag: "Mới",
    colors: ["#111827", "#d1d5db"],
    colorNames: ["Phối đen xám", "Trắng xám"],
    image: "1525966222134-fcfa99b8ae77",
    description: "Cảm hứng đường phố thập niên 90, phối màu tương phản sắc nét, đế đệm giảm chấn di chuyển êm dịu.",
    rating: 4.8,
    reviews: 98
  },
  {
    id: "giay-3",
    code: "PROD-giay-3",
    category: "giay",
    label: "Giày chạy bộ",
    name: "Giày chạy bộ siêu nhẹ Air-Stride Pro",
    price: 1350000,
    oldPrice: 1650000,
    tag: "Xuân hè",
    colors: ["#dc2626", "#1e3a8a", "#000000"],
    colorNames: ["Đỏ cam", "Xanh cobalt", "Đen tuyền"],
    image: "1542291026-7eec264c27ff",
    description: "Đế đệm bọt khí phản hồi năng lượng cao, thân vải dệt nguyên khối thoáng khí cho cự ly 10–21 km.",
    rating: 4.9,
    reviews: 245
  },
  {
    id: "giay-4",
    code: "PROD-giay-4",
    category: "giay",
    label: "Sandal",
    name: "Sandal quai chéo EVA Feather Light",
    price: 350000,
    oldPrice: 420000,
    tag: "",
    colors: ["#78716c", "#1f2937"],
    colorNames: ["Nâu đất", "Đen"],
    image: "1562183241-b937e95585b6",
    description: "Đúc nguyên khối từ nhựa EVA siêu nhẹ không thấm nước, quai ôm êm ái linh hoạt khi đi mưa và dạo phố.",
    rating: 4.6,
    reviews: 42
  }
];

// ── Trạng thái ứng dụng ──
let currentCategory = "all";
let searchKeyword = "";
let currentSort = "default";
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

// ==========================================================================
// RENDER DANH MỤC & SẢN PHẨM
// ==========================================================================
function renderCatalog() {
  let items = PRODUCTS.filter(p => currentCategory === "all" || p.category === currentCategory);
  
  const q = searchKeyword.trim().toLowerCase();
  if (q) {
    items = items.filter(p => 
      (p.name + " " + p.label + " " + p.description + " " + p.code).toLowerCase().includes(q)
    );
  }

  if (currentSort === "price-asc") items.sort((a, b) => a.price - b.price);
  if (currentSort === "price-desc") items.sort((a, b) => b.price - a.price);

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