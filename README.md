# 💰 Personal Expense Tracker

A modern, production-ready web application for managing personal finances. Track income and expenses, visualize spending patterns, and generate detailed financial reports.

## ✨ Features

### Core Functionality
- **User Authentication** - Secure registration, login, and logout with password hashing
- **Dashboard** - Real-time financial overview with key metrics and charts
- **Transaction Management** - Add, edit, and delete income/expense transactions
- **Smart Categories** - Default and custom categories for organizing transactions
- **Financial Reports** - Monthly and yearly summaries with detailed analytics
- **Data Visualization** - Interactive charts using Chart.js
- **CSV Export** - Download financial reports for external analysis
- **Responsive Design** - Mobile-friendly interface that works on all devices

### Analytics & Insights
- Total income and expense tracking
- Monthly and yearly financial summaries
- Category-wise spending breakdown
- Income vs. Expenses trends
- Interactive pie charts and bar charts
- Line charts for historical trends

## 🛠 Technology Stack

### Frontend
- HTML5 & CSS3
- Vanilla JavaScript (No frameworks required)
- Chart.js for visualizations
- Responsive design with mobile support

### Backend
- Python 3.8+
- Flask web framework
- SQLAlchemy ORM
- SQLite database (easily upgradeable to MySQL/PostgreSQL)

### Security
- Password hashing with Werkzeug
- Session-based authentication
- CSRF protection ready
- Input validation and SQL injection prevention

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser

## 🚀 Installation

### Step 1: Clone or Download the Project
```bash
cd expense-tracker
```

### Step 2: Create a Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
```bash
python app.py
```

The application will start at `http://localhost:5000`

## 📂 Project Structure

```
expense-tracker/
├── app.py                    # Main Flask application
├── models.py                 # Database models
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── routes/
│   ├── auth.py              # Authentication routes
│   ├── dashboard.py         # Dashboard routes
│   ├── transactions.py      # Transaction management routes
│   ├── reports.py           # Reports and analytics routes
│   └── api.py               # API endpoints
├── templates/
│   ├── base.html            # Base template with navigation
│   ├── landing.html         # Landing page
│   ├── login.html           # Login page
│   ├── register.html        # Registration page
│   ├── dashboard.html       # Dashboard page
│   ├── transactions.html    # Transactions list
│   ├── add_transaction.html # Add transaction form
│   ├── edit_transaction.html # Edit transaction form
│   ├── reports.html         # Monthly reports
│   ├── yearly_report.html   # Yearly reports
│   └── profile.html         # User profile page
├── static/
│   ├── css/
│   │   └── style.css        # Main stylesheet
│   ├── js/
│   │   └── app.js           # JavaScript functionality
│   └── images/              # Image assets
├── database/
│   └── expense_tracker.db   # SQLite database (auto-created)
└── exports/                 # Directory for CSV exports
```

## 🔐 Default Categories

### Expense Categories
- Food
- Transportation
- Shopping
- Bills
- Healthcare
- Entertainment
- Education
- Other

### Income Categories
- Salary
- Freelancing
- Investments
- Other

Users can create custom categories in addition to these defaults.

## 📖 Usage Guide

### 1. Getting Started
1. Visit `http://localhost:5000`
2. Click "Get Started" to create a new account
3. Fill in username, email, and password
4. Click "Create Account"

### 2. Adding Transactions
1. Go to "Add Transaction" or click "+ Quick Add Expense" on the dashboard
2. Enter the amount
3. Select the category
4. Choose the date
5. Add optional description
6. Click "Add Transaction"

### 3. Viewing Transactions
1. Go to "Transactions" page
2. Filter by type (All, Income, Expense) and category
3. View your transaction history with pagination
4. Click "Edit" to modify or "Delete" to remove a transaction

### 4. Analyzing Finances
1. Go to "Reports" to see monthly analytics
2. View interactive charts:
   - Expenses by Category (Doughnut chart)
   - Income by Category (Doughnut chart)
   - Income vs Expenses Trend (Line chart)
3. Select different months to compare
4. Click "View Yearly Report" for annual summary

### 5. Exporting Data
1. On the Reports page, click "📥 Export CSV"
2. Choose export type (All, Income, Expense)
3. Select the month to export
4. File will download automatically

### 6. Managing Profile
1. Click "Profile" in the navigation
2. View your financial summary
3. See account details
4. Access export and security settings

## 🔧 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/profile` - Get user profile

### Dashboard
- `GET /dashboard/` - View dashboard

### Transactions
- `GET /transactions/` - List all transactions
- `POST /transactions/add` - Add new transaction
- `POST /transactions/<id>/edit` - Edit transaction
- `POST /transactions/<id>/delete` - Delete transaction

### Reports
- `GET /reports/` - View monthly reports
- `GET /reports/yearly` - View yearly reports
- `POST /reports/export/csv` - Export to CSV

### API Routes
- `GET /api/categories` - Get user categories
- `POST /api/categories` - Create category
- `PUT /api/categories/<id>` - Update category
- `DELETE /api/categories/<id>` - Delete category
- `GET /api/dashboard/stats` - Get stats
- `GET /api/dashboard/recent` - Get recent transactions
- `POST /api/transactions/quick` - Quick add transaction

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);
```

### Categories Table
```sql
CREATE TABLE categories (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    category_type VARCHAR(20) NOT NULL,
    color VARCHAR(7) DEFAULT '#3498db',
    is_custom BOOLEAN DEFAULT FALSE,
    created_at DATETIME NOT NULL,
    UNIQUE(user_id, category_name),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    category_id VARCHAR(36) NOT NULL,
    amount FLOAT NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    description VARCHAR(255),
    transaction_date DATE NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(category_id) REFERENCES categories(id)
);
```

## 🔒 Security Features

✅ **Implemented**
- Password hashing using PBKDF2
- Session-based authentication
- Input validation
- SQL injection prevention (via SQLAlchemy ORM)
- CSRF protection support
- Secure session cookies

✨ **Best Practices**
- Never store plain text passwords
- Validate all user inputs
- Use prepared statements
- Implement rate limiting (for production)
- Enable HTTPS (for production)

## 🚀 Production Deployment

### Environment Variables
Create a `.env` file in the project root:

```env
FLASK_ENV=production
SECRET_KEY=your-secure-secret-key-here
DATABASE_URL=sqlite:///expense_tracker.db
```

### Important Security Considerations

1. **Change SECRET_KEY** - Generate a strong secret key for production
2. **Use HTTPS** - Always use HTTPS in production
3. **Database** - Consider upgrading to PostgreSQL or MySQL
4. **Backup** - Regular database backups are essential
5. **Logging** - Implement proper logging and monitoring

### Running with Gunicorn (Production)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Nginx Configuration (Example)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'flask'"
**Solution:** Install dependencies with `pip install -r requirements.txt`

### Issue: "Database is locked"
**Solution:** Ensure only one instance of the app is running

### Issue: "Port 5000 is already in use"
**Solution:** Use different port: `python app.py --port 5001`

### Issue: Charts not displaying
**Solution:** Ensure Chart.js CDN is accessible and JavaScript is enabled

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones (iOS and Android)
- All modern browsers (Chrome, Firefox, Safari, Edge)

## 🎨 Customization

### Changing Colors
Edit CSS variables in `static/css/style.css`:

```css
:root {
    --primary: #667eea;
    --secondary: #764ba2;
    --success: #27ae60;
    --danger: #e74c3c;
    --warning: #f39c12;
    /* ... more colors */
}
```

### Adding Custom Features
1. Create new routes in `routes/` directory
2. Add corresponding templates in `templates/`
3. Update navigation in `base.html`

## 📈 Future Enhancements

- [ ] Two-factor authentication
- [ ] Budget planning and alerts
- [ ] Recurring transactions
- [ ] Bill reminders
- [ ] Mobile app (React Native)
- [ ] Multi-currency support
- [ ] Advanced filtering and search
- [ ] Integration with banking APIs
- [ ] Dark mode theme
- [ ] Data import from other sources

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 💬 Support

For support, email support@expensetracker.com or create an issue in the repository.

## 🎉 Acknowledgments

- Chart.js for beautiful charts
- Flask team for the amazing framework
- SQLAlchemy for robust ORM
- All contributors and testers

---

**Happy Tracking! 💰**

Made with ❤️ for financial freedom
