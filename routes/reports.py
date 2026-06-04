from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from models import db, User, Transaction, Category
from datetime import datetime, timedelta
from functools import wraps
import csv
from io import StringIO

reports_bp = Blueprint('reports', __name__)


def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@reports_bp.route('/', methods=['GET'])
@login_required
def index():
    """Reports dashboard."""
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    selected_month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    selected_year = request.args.get('year', datetime.now().year)

    try:
        year, month = map(int, selected_month.split('-'))
    except (ValueError, AttributeError):
        today = datetime.now()
        year, month = today.year, today.month

    # Calculate month dates
    first_day = datetime(year, month, 1).date()
    if month == 12:
        last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)

    # Get transactions for selected month
    transactions = Transaction.query.filter(
        Transaction.user_id == user.id,
        Transaction.transaction_date >= first_day,
        Transaction.transaction_date <= last_day
    ).order_by(Transaction.transaction_date.desc()).all()

    # Calculate monthly totals
    monthly_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    monthly_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    monthly_balance = monthly_income - monthly_expenses

    # Category-wise breakdown
    income_by_category = db.session.query(
        Category.category_name,
        Category.color,
        db.func.sum(Transaction.amount).label('total')
    ).join(Transaction).filter(
        Transaction.user_id == user.id,
        Transaction.transaction_type == 'income',
        Transaction.transaction_date >= first_day,
        Transaction.transaction_date <= last_day
    ).group_by(Category.id, Category.category_name, Category.color).all()

    expenses_by_category = db.session.query(
        Category.category_name,
        Category.color,
        db.func.sum(Transaction.amount).label('total')
    ).join(Transaction).filter(
        Transaction.user_id == user.id,
        Transaction.transaction_type == 'expense',
        Transaction.transaction_date >= first_day,
        Transaction.transaction_date <= last_day
    ).group_by(Category.id, Category.category_name, Category.color).all()

    # Prepare data for charts
    income_categories = [cat[0] for cat in income_by_category]
    income_amounts = [float(cat[2] or 0) for cat in income_by_category]
    income_colors = [cat[1] for cat in income_by_category]

    expense_categories = [cat[0] for cat in expenses_by_category]
    expense_amounts = [float(cat[2] or 0) for cat in expenses_by_category]
    expense_colors = [cat[1] for cat in expenses_by_category]

    # Get last 12 months data for trend
    today = datetime.now().date()
    months_data = []
    for i in range(11, -1, -1):
        target_date = today - timedelta(days=30*i)
        first_of_month = target_date.replace(day=1)
        if first_of_month.month == 12:
            last_of_month = datetime(first_of_month.year + 1, 1, 1).date() - timedelta(days=1)
        else:
            last_of_month = datetime(first_of_month.year, first_of_month.month + 1, 1).date() - timedelta(days=1)

        month_income = sum(t.amount for t in Transaction.query.filter(
            Transaction.user_id == user.id,
            Transaction.transaction_type == 'income',
            Transaction.transaction_date >= first_of_month,
            Transaction.transaction_date <= last_of_month
        ).all())

        month_expenses = sum(t.amount for t in Transaction.query.filter(
            Transaction.user_id == user.id,
            Transaction.transaction_type == 'expense',
            Transaction.transaction_date >= first_of_month,
            Transaction.transaction_date <= last_of_month
        ).all())

        months_data.append({
            'month': first_of_month.strftime('%B'),
            'income': month_income,
            'expenses': month_expenses
        })

    report_data = {
        'selected_month': selected_month,
        'selected_year': selected_year,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'monthly_balance': monthly_balance,
        'income_categories': income_categories,
        'income_amounts': income_amounts,
        'income_colors': income_colors,
        'expense_categories': expense_categories,
        'expense_amounts': expense_amounts,
        'expense_colors': expense_colors,
        'months_data': months_data,
        'transactions': transactions[:10]  # Last 10 transactions
    }

    return render_template('reports.html', **report_data)


@reports_bp.route('/export/csv', methods=['POST'])
@login_required
def export_csv():
    """Export transactions as CSV."""
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    export_type = request.form.get('type', 'all')
    month = request.form.get('month')

    try:
        query = Transaction.query.filter_by(user_id=user.id)

        if month:
            year, mon = map(int, month.split('-'))
            first_day = datetime(year, mon, 1).date()
            if mon == 12:
                last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                last_day = datetime(year, mon + 1, 1).date() - timedelta(days=1)
            query = query.filter(
                Transaction.transaction_date >= first_day,
                Transaction.transaction_date <= last_day
            )

        if export_type in ['income', 'expense']:
            query = query.filter_by(transaction_type=export_type)

        transactions = query.order_by(Transaction.transaction_date.desc()).all()

        # Create CSV
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Date', 'Category', 'Type', 'Amount', 'Description'])

        for trans in transactions:
            writer.writerow([
                trans.transaction_date.strftime('%Y-%m-%d'),
                trans.category.category_name,
                trans.transaction_type.title(),
                f'{trans.amount:.2f}',
                trans.description or ''
            ])

        csv_content = output.getvalue()
        filename = f'expense-report-{datetime.now().strftime("%Y-%m-%d")}.csv'

        return jsonify({
            'success': True,
            'csv': csv_content,
            'filename': filename
        }), 200

    except Exception as e:
        return jsonify({'error': f'Error exporting data: {str(e)}'}), 500


@reports_bp.route('/yearly', methods=['GET'])
@login_required
def yearly_report():
    """Yearly summary report."""
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    selected_year = request.args.get('year', datetime.now().year, type=int)

    # Get all transactions for the year
    first_day = datetime(selected_year, 1, 1).date()
    last_day = datetime(selected_year, 12, 31).date()

    transactions = Transaction.query.filter(
        Transaction.user_id == user.id,
        Transaction.transaction_date >= first_day,
        Transaction.transaction_date <= last_day
    ).all()

    yearly_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    yearly_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    yearly_balance = yearly_income - yearly_expenses

    # Monthly breakdown
    monthly_breakdown = []
    for month in range(1, 13):
        month_first = datetime(selected_year, month, 1).date()
        if month == 12:
            month_last = datetime(selected_year + 1, 1, 1).date() - timedelta(days=1)
        else:
            month_last = datetime(selected_year, month + 1, 1).date() - timedelta(days=1)

        month_income = sum(t.amount for t in transactions
                          if t.transaction_type == 'income' and month_first <= t.transaction_date <= month_last)
        month_expenses = sum(t.amount for t in transactions
                            if t.transaction_type == 'expense' and month_first <= t.transaction_date <= month_last)

        monthly_breakdown.append({
            'month': datetime(selected_year, month, 1).strftime('%B'),
            'income': month_income,
            'expenses': month_expenses,
            'balance': month_income - month_expenses
        })

    return render_template(
        'yearly_report.html',
        selected_year=selected_year,
        yearly_income=yearly_income,
        yearly_expenses=yearly_expenses,
        yearly_balance=yearly_balance,
        monthly_breakdown=monthly_breakdown
    )
