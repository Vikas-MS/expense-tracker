from flask import Blueprint, render_template, session, redirect, url_for
from models import db, User, Transaction, Category
from datetime import datetime, timedelta
from functools import wraps

dashboard_bp = Blueprint('dashboard', __name__)


def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@dashboard_bp.route('/', methods=['GET'])
@login_required
def index():
    """Dashboard home page."""
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    # Calculate current month dates
    today = datetime.now().date()
    first_day_of_month = today.replace(day=1)
    if today.month == 12:
        last_day_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

    # Get financial data
    total_income = user.get_total_income()
    total_expenses = user.get_total_expenses()
    balance = user.get_balance()

    # Get monthly data
    monthly_income = user.get_total_income(first_day_of_month, last_day_of_month)
    monthly_expenses = user.get_total_expenses(first_day_of_month, last_day_of_month)
    monthly_balance = monthly_income - monthly_expenses

    # Get recent transactions (last 10)
    recent_transactions = Transaction.query.filter_by(user_id=user.id).order_by(
        Transaction.transaction_date.desc(),
        Transaction.created_at.desc()
    ).limit(10).all()

    # Get category-wise expenses for current month
    expenses_by_category = db.session.query(
        Category.category_name,
        db.func.sum(Transaction.amount).label('total')
    ).join(Transaction).filter(
        Transaction.user_id == user.id,
        Transaction.transaction_type == 'expense',
        Transaction.transaction_date >= first_day_of_month,
        Transaction.transaction_date <= last_day_of_month
    ).group_by(Category.id, Category.category_name).all()

    # Prepare dashboard data
    dashboard_data = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'monthly_balance': monthly_balance,
        'recent_transactions': recent_transactions,
        'expenses_by_category': expenses_by_category,
        'today': today.strftime('%B %d, %Y')
    }

    return render_template('dashboard.html', **dashboard_data)
