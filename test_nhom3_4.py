"""Test tự động Nhóm 3 & Nhóm 4 — gọi thẳng vào API đang chạy.

Chạy:
    python test_nhom3_4.py

Yêu cầu:
    pip install requests pillow
    Backend đang chạy tại http://localhost:8000
"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path

try:
    import requests
    from PIL import Image
except ImportError:
    print("Cài thư viện trước:  pip install requests pillow")
    sys.exit(1)

BASE_URL = "http://localhost:8000/api/v1/search/image"

PASS = "\033[92m[PASS]\033[0m"
FAIL = "\033[91m[FAIL]\033[0m"
results: list[tuple[str, bool, str]] = []


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _post(file_bytes: bytes, filename: str = "test.jpg", content_type: str = "image/jpeg"):
    """POST multipart/form-data tới /api/v1/search/image."""
    return requests.post(
        BASE_URL,
        files={"image": (filename, io.BytesIO(file_bytes), content_type)},
        timeout=30,
    )


def _make_real_jpeg(size: tuple[int, int] = (200, 200)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", size, color=(180, 100, 50)).save(buf, format="JPEG")
    return buf.getvalue()


def check(label: str, resp, expected_status: int, extra_check=None):
    ok = resp.status_code == expected_status
    if ok and extra_check:
        ok = extra_check(resp)
    tag = PASS if ok else FAIL
    note = f"HTTP {resp.status_code}"
    if not ok:
        note += f" (expected {expected_status})"
    if extra_check and ok is False:
        note += f" | body: {resp.text[:120]}"
    print(f"  {tag} {label}  — {note}")
    results.append((label, ok, note))


# ─────────────────────────────────────────────────────────────────────────────
# Nhóm 4 — Lỗi kỹ thuật
# ─────────────────────────────────────────────────────────────────────────────

def test_group4():
    print("\n━━━ Nhóm 4: Lỗi kỹ thuật ━━━")

    # 4.4a — File 0-byte
    resp = _post(b"", "empty_0_byte.jpg")
    check("4.4a  File 0-byte → HTTP 400", resp, 400,
          lambda r: "empty" in r.text.lower() or "0 byte" in r.text.lower())

    # 4.4b — File PDF giả mạo đuôi .jpg
    fake_pdf = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"
    resp = _post(fake_pdf, "fake_pdf.jpg")
    check("4.4b  PDF đổi đuôi .jpg → HTTP 400", resp, 400,
          lambda r: "magic" in r.text.lower() or "content does not match" in r.text.lower()
                    or "pdf" in r.text.lower() or "400" in str(r.status_code))

    # 4.4c — File text giả mạo đuôi .jpg
    fake_txt = "Day khong phai la anh. Chi la file text doi duoi thanh .jpg\n".encode()
    resp = _post(fake_txt, "fake_txt.jpg")
    check("4.4c  Text đổi đuôi .jpg → HTTP 400", resp, 400)

    # 4.3 — File > 10 MB
    print("  (Đang tạo file >10 MB để test 4.3, chờ vài giây...)")
    large_bytes = _make_oversized_jpeg_bytes()
    if large_bytes:
        resp = _post(large_bytes, "oversize.jpg")
        check("4.3   File >10 MB → HTTP 413", resp, 413)
    else:
        print(f"  \033[93m[SKIP]\033[0m 4.3  Không tạo được file >10 MB")


def _make_oversized_jpeg_bytes() -> bytes | None:
    """Tạo JPEG ngẫu nhiên >10 MB (nén kém nên dễ vượt ngưỡng)."""
    target = 11 * 1024 * 1024
    side = 1500
    for _ in range(8):
        buf = io.BytesIO()
        Image.frombytes("RGB", (side, side), os.urandom(side * side * 3)).save(
            buf, format="JPEG", quality=99, subsampling=0
        )
        data = buf.getvalue()
        if len(data) >= target:
            return data
        side += 500
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Nhóm 3 — Kết quả gượng ép (đồ vật ngoài danh mục)
# ─────────────────────────────────────────────────────────────────────────────

def test_group3():
    print("\n━━━ Nhóm 3: Kết quả gượng ép ━━━")

    # Tạo ảnh tổng hợp mô phỏng vật thể đơn sắc (không phải thời trang)
    # → không có embedding thực trong DB → similarity thấp → results=[]
    def solid_color_jpeg(color) -> bytes:
        buf = io.BytesIO()
        Image.new("RGB", (256, 256), color=color).save(buf, format="JPEG", quality=95)
        return buf.getvalue()

    test_images = [
        ("3.3a  Ảnh đen tuyền (không phải thời trang)", solid_color_jpeg((0, 0, 0))),
        ("3.3b  Ảnh trắng tuyền", solid_color_jpeg((255, 255, 255))),
        ("3.3c  Ảnh xám", solid_color_jpeg((128, 128, 128))),
    ]

    for label, img_bytes in test_images:
        resp = _post(img_bytes, "synthetic.jpg")
        if resp.status_code == 200:
            body = resp.json()
            result_count = len(body.get("results", []))
            has_message = bool(body.get("no_results_message"))
            ok = result_count == 0 and has_message
            tag = PASS if ok else FAIL
            note = (
                f"HTTP 200, results={result_count}, "
                f"no_results_message={'✓' if has_message else '✗ (thiếu)'}"
            )
            print(f"  {tag} {label}  — {note}")
            results.append((label, ok, note))
        else:
            check(label, resp, 200)

    # Ảnh giả là JPEG hợp lệ nhưng nội dung là noise → hệ thống không nên crash
    print("\n  [INFO] Test ảnh noise ngẫu nhiên (valid JPEG, nội dung vô nghĩa)")
    noise_buf = io.BytesIO()
    Image.frombytes("RGB", (64, 64), os.urandom(64 * 64 * 3)).save(noise_buf, format="JPEG")
    noise_bytes = noise_buf.getvalue()
    resp = _post(noise_bytes, "noise.jpg")
    ok = resp.status_code in (200, 422)  # 200 với results=[] hoặc lỗi validation
    tag = PASS if ok else FAIL
    note = f"HTTP {resp.status_code} (không crash 500)"
    if resp.status_code == 200:
        body = resp.json()
        note += f", results={len(body.get('results', []))}"
    print(f"  {tag} 3.3d  Noise JPEG hợp lệ không crash  — {note}")
    results.append(("3.3d  Noise JPEG không crash", ok, note))


# ─────────────────────────────────────────────────────────────────────────────
# Ảnh hợp lệ — đảm bảo API vẫn hoạt động bình thường (sanity check)
# ─────────────────────────────────────────────────────────────────────────────

def test_sanity():
    print("\n━━━ Sanity: Ảnh JPEG hợp lệ phải trả 200 ━━━")
    resp = _post(_make_real_jpeg(), "valid.jpg")
    ok = resp.status_code == 200
    tag = PASS if ok else FAIL
    body_preview = resp.text[:80] if not ok else ""
    print(f"  {tag} JPEG hợp lệ → HTTP 200  — HTTP {resp.status_code} {body_preview}")
    results.append(("Sanity: JPEG hợp lệ → 200", ok, f"HTTP {resp.status_code}"))

    # PNG
    png_buf = io.BytesIO()
    Image.new("RGB", (100, 100), (50, 150, 200)).save(png_buf, format="PNG")
    resp = _post(png_buf.getvalue(), "valid.png", "image/png")
    ok = resp.status_code == 200
    tag = PASS if ok else FAIL
    print(f"  {tag} PNG hợp lệ → HTTP 200  — HTTP {resp.status_code}")
    results.append(("Sanity: PNG hợp lệ → 200", ok, f"HTTP {resp.status_code}"))

    # WebP
    webp_buf = io.BytesIO()
    Image.new("RGB", (100, 100), (200, 80, 30)).save(webp_buf, format="WEBP")
    resp = _post(webp_buf.getvalue(), "valid.webp", "image/webp")
    ok = resp.status_code == 200
    tag = PASS if ok else FAIL
    print(f"  {tag} WebP hợp lệ → HTTP 200  — HTTP {resp.status_code}")
    results.append(("Sanity: WebP hợp lệ → 200", ok, f"HTTP {resp.status_code}"))


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  Test Nhóm 3 & 4 — AI Shopping Assistants")
    print(f"  API: {BASE_URL}")
    print("=" * 60)

    # Kiểm tra server có sẵn không
    try:
        r = requests.get("http://localhost:8000/health", timeout=5)
    except Exception:
        try:
            r = requests.get("http://localhost:8000/docs", timeout=5)
        except Exception:
            print("\n❌ Không kết nối được tới http://localhost:8000")
            print("   Hãy chắc chắn backend đang chạy (start_app.bat)")
            sys.exit(1)

    test_sanity()
    test_group4()
    test_group3()

    # Tổng kết
    print("\n" + "=" * 60)
    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    print(f"  Kết quả: {passed}/{total} test PASS")
    if passed == total:
        print("  \033[92m✓ Tất cả test đều PASS!\033[0m")
    else:
        print("  \033[91m✗ Có test FAIL — xem chi tiết ở trên.\033[0m")
    print("=" * 60)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
