@echo off
REM Setup script for Personal Expense Tracker (Windows)

echo.
echo 🚀 Setting up Personal Expense Tracker...
echo.

REM Check Python version
python --version
echo.

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo ⚙️  Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please update .env with your configuration
)

REM Create database directory
echo 🗂️  Creating database directory...
if not exist "database" mkdir database
if not exist "exports" mkdir exports

REM Initialize database
echo 💾 Initializing database...
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('✅ Database initialized successfully!')"

echo.
echo ✨ Setup completed successfully!
echo.
echo 🎯 Next steps:
echo 1. Update .env file with your configuration (if needed)
echo 2. Run the application: python app.py
echo 3. Open http://localhost:5000 in your browser
echo.
echo Happy tracking! 💰
echo.
pause
