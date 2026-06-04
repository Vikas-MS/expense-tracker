from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from models import db, User, Transaction, Category
from datetime import datetime
from functools import wraps

transactions_bp = Blueprint('transactions', __name__)


def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@transactions_bp.route('/', methods=['GET'])
@login_required
def list_transactions():
    """List all transactions."""
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    # Get filter parameters
    transaction_type = request.args.get('type', 'all')
    category_id = request.args.get('category', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20

    query = Transaction.query.filter_by(user_id=user.id)

    if transaction_type in ['income', 'expense']:
        query = query.filter_by(transaction_type=transaction_type)

    if category_id:
        query = query.filter_by(category_id=category_id)

    # Pagination
    transactions = query.order_by(
        Transaction.transaction_date.desc(),
        Transaction.created_at.desc()
    ).paginate(page=page, per_page=per_page)

    # Get categories for filter
    categories = Category.query.filter_by(user_id=user.id).all()

    return render_template(
        'transactions.html',
        transactions=transactions,
        categories=categories,
        selected_type=transaction_type,
        selected_category=category_id
    )


@transactions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    """Add new transaction."""
    if request.method == 'POST':
        try:
            user = User.query.get(session['user_id'])
            if not user:
                return jsonify({'error': 'User not found'}), 404

            # Get form data
            amount = request.form.get('amount', '').strip()
            category_id = request.form.get('category_id', '').strip()
            transaction_type = request.form.get('type', '').strip()
            description = request.form.get('description', '').strip()
            transaction_date = request.form.get('transaction_date', '').strip()

            # Validation
            if not all([amount, category_id, transaction_type]):
                return jsonify({'error': 'Amount, category, and type are required'}), 400

            try:
                amount = float(amount)
                if amount <= 0:
                    return jsonify({'error': 'Amount must be greater than 0'}), 400
            except ValueError:
                return jsonify({'error': 'Invalid amount'}), 400

            if transaction_type not in ['income', 'expense']:
                return jsonify({'error': 'Invalid transaction type'}), 400

            # Verify category belongs to user
            category = Category.query.filter_by(id=category_id, user_id=user.id).first()
            if not category:
                return jsonify({'error': 'Invalid category'}), 404

            # Parse date
            try:
                if transaction_date:
                    parsed_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
                else:
                    parsed_date = datetime.now().date()
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400

            # Create transaction
            transaction = Transaction(
                user_id=user.id,
                category_id=category_id,
                amount=amount,
                transaction_type=transaction_type,
                description=description,
                transaction_date=parsed_date
            )

            db.session.add(transaction)
            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Transaction added successfully',
                'transaction': transaction.to_dict()
            }), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error adding transaction: {str(e)}'}), 500

    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    categories = Category.query.filter_by(user_id=user.id).all()
    return render_template('add_transaction.html', categories=categories)


@transactions_bp.route('/<transaction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    """Edit transaction."""
    user = User.query.get(session['user_id'])
    if not user:
        return redirect(url_for('auth.login'))

    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user.id).first()
    if not transaction:
        return redirect(url_for('transactions.list_transactions'))

    if request.method == 'POST':
        try:
            amount = request.form.get('amount', '').strip()
            category_id = request.form.get('category_id', '').strip()
            description = request.form.get('description', '').strip()
            transaction_date = request.form.get('transaction_date', '').strip()

            if not all([amount, category_id]):
                return jsonify({'error': 'Amount and category are required'}), 400

            try:
                amount = float(amount)
                if amount <= 0:
                    return jsonify({'error': 'Amount must be greater than 0'}), 400
            except ValueError:
                return jsonify({'error': 'Invalid amount'}), 400

            # Verify category belongs to user
            category = Category.query.filter_by(id=category_id, user_id=user.id).first()
            if not category:
                return jsonify({'error': 'Invalid category'}), 404

            try:
                if transaction_date:
                    parsed_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
                else:
                    parsed_date = transaction.transaction_date
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400

            transaction.amount = amount
            transaction.category_id = category_id
            transaction.description = description
            transaction.transaction_date = parsed_date

            db.session.commit()

            return jsonify({
                'success': True,
                'message': 'Transaction updated successfully',
                'transaction': transaction.to_dict()
            }), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error updating transaction: {str(e)}'}), 500

    categories = Category.query.filter_by(user_id=user.id).all()
    return render_template('edit_transaction.html', transaction=transaction, categories=categories)


@transactions_bp.route('/<transaction_id>/delete', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    """Delete transaction."""
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'User not found'}), 404

    transaction = Transaction.query.filter_by(id=transaction_id, user_id=user.id).first()
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404

    try:
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Transaction deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting transaction: {str(e)}'}), 500
