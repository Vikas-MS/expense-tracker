#!/bin/bash
# Project verification script

echo ""
echo "========================================"
echo "Personal Expense Tracker - Verification"
echo "========================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
echo -n "🐍 Checking Python... "
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1)
    echo -e "${GREEN}✓${NC} $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python not found"
    exit 1
fi

# Check virtual environment
echo -n "🔧 Checking virtual environment... "
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Found"
else
    echo -e "${YELLOW}⚠${NC} Not created yet (run setup.sh first)"
fi

# Check key files
echo ""
echo "📋 Checking key files:"

files=(
    "app.py"
    "models.py"
    "config.py"
    "requirements.txt"
    "static/css/style.css"
    "static/js/app.js"
    "templates/base.html"
    "routes/auth.py"
    "routes/dashboard.py"
    "routes/transactions.py"
    "routes/reports.py"
    "routes/api.py"
)

missing_files=0
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${RED}✗${NC} $file (MISSING)"
        ((missing_files++))
    fi
done

# Check templates
echo ""
echo "📄 HTML Templates:"
templates=(
    "landing.html"
    "login.html"
    "register.html"
    "dashboard.html"
    "transactions.html"
    "add_transaction.html"
    "edit_transaction.html"
    "reports.html"
    "yearly_report.html"
    "profile.html"
)

for template in "${templates[@]}"; do
    if [ -f "templates/$template" ]; then
        echo -e "  ${GREEN}✓${NC} $template"
    else
        echo -e "  ${RED}✗${NC} $template (MISSING)"
        ((missing_files++))
    fi
done

# Check directories
echo ""
echo "📁 Checking directories:"
dirs=("database" "exports" "static/css" "static/js" "routes" "templates")

for dir in "${dirs[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "  ${GREEN}✓${NC} $dir"
    else
        echo -e "  ${YELLOW}⚠${NC} $dir (will be created on first run)"
    fi
done

# Summary
echo ""
echo "========================================"
if [ $missing_files -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "🚀 Ready to run!"
    echo ""
    echo "Next steps:"
    echo "1. Run: source venv/bin/activate  (or venv\\Scripts\\activate on Windows)"
    echo "2. Run: python app.py"
    echo "3. Open: http://localhost:5000"
else
    echo -e "${RED}✗ $missing_files file(s) missing!${NC}"
    echo "Please ensure all files are present."
fi

echo ""
