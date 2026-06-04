# ⚡ Quick Start Guide

Get the Personal Expense Tracker up and running in 5 minutes!

## 🚀 Installation

### Option 1: Automatic Setup (Recommended)

**Windows:**
```bash
setup.bat
```

**macOS/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir database
mkdir exports

# Run the app
python app.py
```

## 🌐 Access the App

Open your browser and go to:
```
http://localhost:5000
```

## 📚 First Steps

1. **Register**: Click "Get Started" and create an account
2. **Add Transaction**: Click "+ Quick Add Expense" or go to "Add Transaction"
3. **View Dashboard**: See your financial overview with charts
4. **Explore Reports**: Check "Reports" for detailed analytics

## 🔥 Common Tasks

### Add a Transaction
```
Dashboard → Quick Add Expense
or
Transactions → + Add Transaction
```

### View Your Finances
```
Dashboard → See overview and recent transactions
Reports → View charts and trends
```

### Export Data
```
Reports → Export CSV → Choose type and month
```

### Manage Categories
Categories are automatically created. Create custom ones in future versions!

## 🛠 Configuration

Create a `.env` file (copy from `.env.example`):
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
```

For production, use:
```env
FLASK_ENV=production
SECRET_KEY=generate-strong-secret-key
DATABASE_URL=your-database-url
```

## 📱 Features at a Glance

| Feature | How to Access |
|---------|---------------|
| Dashboard | Home page after login |
| Add Transaction | Main navigation or dashboard |
| View Transactions | Transactions → All Transactions |
| Monthly Reports | Reports → Monthly Analytics |
| Yearly Reports | Reports → Yearly Summary |
| Export to CSV | Reports → Export button |
| User Profile | Profile in navigation |

## 🔒 Security Tips

✅ Change default password (when password reset is available)
✅ Keep SECRET_KEY secure
✅ Use HTTPS in production
✅ Regular database backups

## ⚠️ Troubleshooting

**Port 5000 already in use:**
```bash
python app.py --port 5001
```

**Module not found error:**
```bash
pip install -r requirements.txt
```

**Database error:**
```bash
# Delete the database and restart
rm database/expense_tracker.db
python app.py
```

## 📊 Sample Data

To test the app:
1. Create an account
2. Add a few income transactions (Salary category)
3. Add several expense transactions (different categories)
4. Go to Reports to see charts and analytics

## 🎯 Next Steps

- Explore the Dashboard
- Add your first transaction
- Check out the Reports
- Download a CSV export
- Customize categories

## 📞 Need Help?

1. Check README.md for detailed documentation
2. Review API endpoints in README.md
3. Check browser console for JavaScript errors
4. Verify database is created in `/database` folder

## 🚀 Ready to Deploy?

For production deployment:

1. Set `FLASK_ENV=production`
2. Generate strong `SECRET_KEY`
3. Use PostgreSQL/MySQL instead of SQLite
4. Deploy with Gunicorn and Nginx
5. Enable HTTPS

See README.md for production deployment guide.

---

**Happy Tracking! 💰**

Enjoy managing your finances with Personal Expense Tracker!
