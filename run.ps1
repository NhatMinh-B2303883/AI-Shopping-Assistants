# ========================================================
# EAST & SOUL — AI SHOPPING ASSISTANTS
# Script khởi chạy toàn bộ hệ thống: Backend + Frontend
# ========================================================

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "      EAST & SOUL — AI SHOPPING ASSISTANTS             " -ForegroundColor Cyan
Write-Host "      Khoi chay he thong Backend + Frontend            " -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Khởi động Database PostgreSQL + pgvector và Backend FastAPI qua Docker Compose
Write-Host "[1/3] Khoi dong Database va Backend (Docker Compose)..." -ForegroundColor Yellow
docker compose up -d

# 2. Đợi Backend khởi động và kiểm tra sức khỏe API
Write-Host "[2/3] Kiem tra Backend tai http://localhost:8000/health ..." -ForegroundColor Yellow
Start-Sleep -Seconds 4

try {
    $res = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 3 -ErrorAction SilentlyContinue
    if ($res.status -eq "ok") {
        Write-Host "  -> Backend da SAN SANG hoat dong! (status: ok)" -ForegroundColor Green
    }
} catch {
    Write-Host "  -> Backend dang trong tien trinh khoi tao..." -ForegroundColor Gray
}

# 3. Mở trình duyệt và khởi chạy Frontend trên cổng 3000
Write-Host ""
Write-Host "[3/3] Mo trinh duyet va khoi chay Frontend Web tai http://localhost:3000 ..." -ForegroundColor Yellow
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "  Backend API : http://localhost:8000" -ForegroundColor White
Write-Host "  Swagger UI  : http://localhost:8000/docs" -ForegroundColor White
Write-Host "  Frontend PC : http://localhost:3000" -ForegroundColor White
Write-Host "  WiFi Mobile : http://192.168.2.26:3000" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Green

Write-Host "  Nhan Ctrl + C de dung may chu Frontend." -ForegroundColor Gray
Write-Host ""

python -m http.server 3000 --directory frontend
