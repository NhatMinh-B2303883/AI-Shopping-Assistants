@echo off
chcp 65001 >nul
echo ========================================================
echo       EAST and SOUL - AI SHOPPING ASSISTANTS
echo       Khoi chay toan bo he thong: Backend + Frontend
echo ========================================================
echo.

echo [1/3] Kiem tra va khoi dong Database + Backend (Docker)...
docker compose up -d

echo.
echo [2/3] Cho Backend khoi dong hoan tat...
timeout /t 5 /nobreak >nul

echo.
echo [3/3] Mo trinh duyet va khoi chay Frontend tai http://localhost:3000 ...
start http://localhost:3000

echo.
echo ========================================================
echo  Backend API : http://localhost:8000
echo  Swagger UI  : http://localhost:8000/docs
echo  Frontend Web: http://localhost:3000
echo ========================================================
echo  Nhan Ctrl + C de dung may chu Frontend.
echo.

python -m http.server 3000 --directory frontend
pause
