from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, User, Category
from functools import wraps
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route('/', methods=['GET'])
def landing():
    """Landing page."""
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return render_template('landing.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        if not all([username, email, password, confirm_password]):
            return jsonify({'error': 'All fields are required'}), 400

        if len(username) < 3:
            return jsonify({'error': 'Username must be at least 3 characters'}), 400

        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400

        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400

        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400

        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400

        try:
            # Create new user
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()

            # Create default categories for new user
            default_expense_categories = ['Food', 'Transportation', 'Shopping', 'Bills', 'Healthcare', 'Entertainment', 'Education', 'Other']
            default_income_categories = ['Salary', 'Freelancing', 'Investments', 'Other']

            colors_expense = ['#e74c3c', '#3498db', '#9b59b6', '#f39c12', '#1abc9c', '#27ae60', '#2c3e50', '#95a5a6']
            colors_income = ['#27ae60', '#f39c12', '#2980b9', '#8e44ad']

            for i, cat_name in enumerate(default_expense_categories):
                category = Category(
                    user_id=user.id,
                    category_name=cat_name,
                    category_type='expense',
                    color=colors_expense[i],
                    is_custom=False
                )
                db.session.add(category)

            for i, cat_name in enumerate(default_income_categories):
                category = Category(
                    user_id=user.id,
                    category_name=cat_name,
                    category_type='income',
                    color=colors_income[i],
                    is_custom=False
                )
                db.session.add(category)

            db.session.commit()

            return jsonify({'success': True, 'message': 'Registration successful! Please login.'}), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Registration failed: {str(e)}'}), 500

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid username or password'}), 401

        session.permanent = True
        session['user_id'] = user.id
        session['username'] = user.username
        session['email'] = user.email

        return jsonify({'success': True, 'message': 'Login successful!'}), 200

    return render_template('login.html')


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """User logout."""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'}), 200


@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """User profile page."""
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    user_data = {
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.strftime('%B %d, %Y'),
        'total_income': user.get_total_income(),
        'total_expenses': user.get_total_expenses(),
        'balance': user.get_balance()
    }

    return render_template('profile.html', user=user_data)
