#!/bin/bash
# Setup script for Personal Expense Tracker

echo "🚀 Setting up Personal Expense Tracker..."

# Check Python version
python_version=$(python --version 2>&1)
echo "Using: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "⚙️  Activating virtual environment..."
if [ -f "venv/Scripts/activate" ]; then
    # Windows
    source venv/Scripts/activate
else
    # macOS/Linux
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Create database directory
echo "🗂️  Creating database directory..."
mkdir -p database
mkdir -p exports

# Initialize database
echo "💾 Initializing database..."
python -c "
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print('✅ Database initialized successfully!')
"

echo ""
echo "✨ Setup completed successfully!"
echo ""
echo "🎯 Next steps:"
echo "1. Update .env file with your configuration (if needed)"
echo "2. Activate virtual environment:"
if [ -f "venv/Scripts/activate" ]; then
    echo "   Windows: venv\\Scripts\\activate"
else
    echo "   macOS/Linux: source venv/bin/activate"
fi
echo "3. Run the application: python app.py"
echo "4. Open http://localhost:5000 in your browser"
echo ""
echo "Happy tracking! 💰"
