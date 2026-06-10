from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from models import User, Transaction, Category
from db import get_session
from datetime import datetime
from functools import wraps
from utils.bills import (
    save_bill, delete_bill_file, apply_bill_data, clear_bill_data, get_user_bill_dir
)
import math
import os

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
    db_s = get_session()
    try:
        user = db_s.get(User, session['user_id'])
        if not user:
            return redirect(url_for('auth.login'))

        # Get filter parameters
        transaction_type = request.args.get('type', 'all')
        category_id = request.args.get('category', '')
        page = request.args.get('page', 1, type=int)
        per_page = 20

        query = db_s.query(Transaction).filter(Transaction.user_id == user.id)

        if transaction_type in ['income', 'expense']:
            query = query.filter(Transaction.transaction_type == transaction_type)

        if category_id:
            query = query.filter(Transaction.category_id == category_id)

        # Pagination (manual)
        total = query.count()
        items = query.order_by(
            Transaction.transaction_date.desc(),
            Transaction.created_at.desc()
        ).offset((page - 1) * per_page).limit(per_page).all()

        class Pagination:
            def __init__(self, items, page, per_page, total):
                self.items = items
                self.page = page
                self.per_page = per_page
                self.total = total
                self.pages = max(1, math.ceil(total / per_page))

            @property
            def has_prev(self):
                return self.page > 1

            @property
            def has_next(self):
                return self.page < self.pages

            @property
            def prev_num(self):
                return self.page - 1 if self.has_prev else None

            @property
            def next_num(self):
                return self.page + 1 if self.has_next else None

            def iter_pages(self):
                return range(1, self.pages + 1)

        transactions = Pagination(items, page, per_page, total)

        # Get categories for filter
        categories = db_s.query(Category).filter(Category.user_id == user.id).all()

        return render_template(
            'transactions.html',
            transactions=transactions,
            categories=categories,
            selected_type=transaction_type,
            selected_category=category_id
        )
    finally:
        db_s.close()


@transactions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    """Add new transaction."""
    if request.method == 'POST':
        try:
            db_s = get_session()
            user = db_s.get(User, session['user_id'])
            if not user:
                db_s.close()
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
            category = db_s.query(Category).filter(
                Category.id == category_id, Category.user_id == user.id
            ).first()
            if not category:
                db_s.close()
                return jsonify({'error': 'Invalid category'}), 404

            # Parse date
            try:
                if transaction_date:
                    parsed_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
                else:
                    parsed_date = datetime.now().date()
            except ValueError:
                return jsonify({'error': 'Invalid date format'}), 400

            bill_file = request.files.get('bill')

            # Create transaction
            transaction = Transaction(
                user_id=user.id,
                category_id=category_id,
                amount=amount,
                transaction_type=transaction_type,
                description=description,
                transaction_date=parsed_date
            )

            db_s.add(transaction)
            db_s.flush()

            if bill_file and bill_file.filename:
                try:
                    bill_data = save_bill(bill_file, user.id)
                    apply_bill_data(transaction, bill_data)
                except ValueError as e:
                    db_s.rollback()
                    db_s.close()
                    return jsonify({'error': str(e)}), 400

            db_s.commit()

            try:
                return jsonify({
                    'success': True,
                    'message': 'Transaction added successfully',
                    'transaction': transaction.to_dict()
                }), 201
            finally:
                db_s.close()

        except Exception as e:
            db_s.rollback()
            db_s.close()
            return jsonify({'error': f'Error adding transaction: {str(e)}'}), 500

    db_s = get_session()
    user = db_s.get(User, session['user_id'])
    if not user:
        db_s.close()
        return redirect(url_for('auth.login'))

    categories = db_s.query(Category).filter(Category.user_id == user.id).all()
    db_s.close()
    return render_template('add_transaction.html', categories=categories)


@transactions_bp.route('/<transaction_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    """Edit transaction."""
    db_s = get_session()
    user = db_s.get(User, session['user_id'])
    if not user:
        db_s.close()
        return redirect(url_for('auth.login'))

    transaction = db_s.query(Transaction).filter(
        Transaction.id == transaction_id, Transaction.user_id == user.id
    ).first()
    if not transaction:
        db_s.close()
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
            category = db_s.query(Category).filter(
                Category.id == category_id, Category.user_id == user.id
            ).first()
            if not category:
                db_s.close()
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

            remove_bill = request.form.get('remove_bill') == 'true'
            bill_file = request.files.get('bill')

            if remove_bill and transaction.bill_filename:
                delete_bill_file(user.id, transaction.bill_filename)
                clear_bill_data(transaction)
            elif bill_file and bill_file.filename:
                try:
                    if transaction.bill_filename:
                        delete_bill_file(user.id, transaction.bill_filename)
                    bill_data = save_bill(bill_file, user.id)
                    apply_bill_data(transaction, bill_data)
                except ValueError as e:
                    db_s.rollback()
                    db_s.close()
                    return jsonify({'error': str(e)}), 400

            try:
                db_s.commit()
                return jsonify({
                    'success': True,
                    'message': 'Transaction updated successfully',
                    'transaction': transaction.to_dict()
                }), 200
            except Exception as e:
                db_s.rollback()
                return jsonify({'error': f'Error updating transaction: {str(e)}'}), 500
            finally:
                db_s.close()

        except Exception as e:
            db_s.rollback()
            db_s.close()
            return jsonify({'error': f'Error updating transaction: {str(e)}'}), 500
    categories = db_s.query(Category).filter(Category.user_id == user.id).all()
    db_s.close()
    return render_template('edit_transaction.html', transaction=transaction, categories=categories)


@transactions_bp.route('/<transaction_id>/delete', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    """Delete transaction."""
    db_s = get_session()
    user = db_s.get(User, session['user_id'])
    if not user:
        db_s.close()
        return jsonify({'error': 'User not found'}), 404

    transaction = db_s.query(Transaction).filter(
        Transaction.id == transaction_id, Transaction.user_id == user.id
    ).first()
    if not transaction:
        db_s.close()
        return jsonify({'error': 'Transaction not found'}), 404

    try:
        if transaction.bill_filename:
            delete_bill_file(user.id, transaction.bill_filename)
        db_s.delete(transaction)
        db_s.commit()
        return jsonify({'success': True, 'message': 'Transaction deleted successfully'}), 200
    except Exception as e:
        db_s.rollback()
        return jsonify({'error': f'Error deleting transaction: {str(e)}'}), 500
    finally:
        db_s.close()


@transactions_bp.route('/<transaction_id>/bill', methods=['GET'])
@login_required
def view_bill(transaction_id):
    """View or download a transaction bill attachment."""
    db_s = get_session()
    try:
        user = db_s.get(User, session['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404

        transaction = db_s.query(Transaction).filter(
            Transaction.id == transaction_id, Transaction.user_id == user.id
        ).first()
        if not transaction or not transaction.bill_filename:
            return jsonify({'error': 'Bill not found'}), 404

        bill_dir = get_user_bill_dir(user.id)
        filepath = os.path.join(bill_dir, transaction.bill_filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'Bill file not found'}), 404

        download = request.args.get('download') == '1'
        return send_from_directory(
            bill_dir,
            transaction.bill_filename,
            mimetype=transaction.bill_mime_type,
            as_attachment=download,
            download_name=transaction.bill_original_name or transaction.bill_filename,
        )
    finally:
        db_s.close()
