@echo off
echo ==========================================
echo    Django Migration Management Script
echo ==========================================
echo.

cd backend

echo [1/4] Checking for new migrations...
python manage.py makemigrations --dry-run --check
if %ERRORLEVEL% neq 0 (
    echo.
    echo [INFO] New migrations detected. Creating them...
    python manage.py makemigrations
)

echo.
echo [2/4] Applying all migrations...
python manage.py migrate

echo.
echo [3/4] Showing migration status...
python manage.py showmigrations

echo.
echo [4/4] Migration management completed successfully!
echo.
echo ==========================================
echo    All migrations have been applied
echo ==========================================

cd ..
pause 