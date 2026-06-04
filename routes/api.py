from flask import Blueprint, request, session, jsonify
from models import db, User, Category, Transaction
from datetime import datetime
from functools import wraps

api_bp = Blueprint('api', __name__)


def token_required(f):
    """Decorator to require user session."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function


@api_bp.route('/categories', methods=['GET'])
@token_required
def get_categories():
    """Get all user categories."""
    user_id = session['user_id']
    category_type = request.args.get('type', '')

    query = Category.query.filter_by(user_id=user_id)
    if category_type in ['income', 'expense']:
        query = query.filter_by(category_type=category_type)

    categories = query.all()
    return jsonify([cat.to_dict() for cat in categories]), 200


@api_bp.route('/categories', methods=['POST'])
@token_required
def create_category():
    """Create new category."""
    user_id = session['user_id']
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    category_name = data.get('category_name', '').strip()
    category_type = data.get('category_type', '').strip()
    color = data.get('color', '#3498db')

    if not category_name or not category_type:
        return jsonify({'error': 'Category name and type are required'}), 400

    if category_type not in ['income', 'expense']:
        return jsonify({'error': 'Invalid category type'}), 400

    if len(category_name) > 100:
        return jsonify({'error': 'Category name is too long'}), 400

    # Check if category already exists
    if Category.query.filter_by(user_id=user_id, category_name=category_name).first():
        return jsonify({'error': 'Category already exists'}), 409

    try:
        category = Category(
            user_id=user_id,
            category_name=category_name,
            category_type=category_type,
            color=color,
            is_custom=True
        )
        db.session.add(category)
        db.session.commit()
        return jsonify(category.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error creating category: {str(e)}'}), 500


@api_bp.route('/categories/<category_id>', methods=['PUT'])
@token_required
def update_category(category_id):
    """Update category."""
    user_id = session['user_id']
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()

    if not category:
        return jsonify({'error': 'Category not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'category_name' in data:
        category.category_name = data['category_name'].strip()

    if 'color' in data:
        category.color = data['color']

    try:
        db.session.commit()
        return jsonify(category.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error updating category: {str(e)}'}), 500


@api_bp.route('/categories/<category_id>', methods=['DELETE'])
@token_required
def delete_category(category_id):
    """Delete category (only custom categories)."""
    user_id = session['user_id']
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()

    if not category:
        return jsonify({'error': 'Category not found'}), 404

    if not category.is_custom:
        return jsonify({'error': 'Cannot delete default categories'}), 403

    # Check if category has transactions
    if Transaction.query.filter_by(category_id=category_id).first():
        return jsonify({'error': 'Cannot delete category with transactions'}), 409

    try:
        db.session.delete(category)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Category deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting category: {str(e)}'}), 500


@api_bp.route('/dashboard/stats', methods=['GET'])
@token_required
def get_dashboard_stats():
    """Get dashboard statistics."""
    user_id = session['user_id']
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'total_income': user.get_total_income(),
        'total_expenses': user.get_total_expenses(),
        'balance': user.get_balance()
    }), 200


@api_bp.route('/dashboard/recent', methods=['GET'])
@token_required
def get_recent_transactions():
    """Get recent transactions."""
    user_id = session['user_id']
    limit = request.args.get('limit', 10, type=int)

    transactions = Transaction.query.filter_by(user_id=user_id).order_by(
        Transaction.transaction_date.desc(),
        Transaction.created_at.desc()
    ).limit(limit).all()

    return jsonify([trans.to_dict() for trans in transactions]), 200


@api_bp.route('/transactions/quick', methods=['POST'])
@token_required
def quick_add_transaction():
    """Quick add transaction from dashboard."""
    user_id = session['user_id']
    user = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    amount = data.get('amount')
    category_id = data.get('category_id')
    description = data.get('description', '')

    if not amount or not category_id:
        return jsonify({'error': 'Amount and category are required'}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid amount'}), 400

    # Verify category
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    try:
        transaction = Transaction(
            user_id=user_id,
            category_id=category_id,
            amount=amount,
            transaction_type=category.category_type,
            description=description,
            transaction_date=datetime.now().date()
        )
        db.session.add(transaction)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Transaction added',
            'transaction': transaction.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error adding transaction: {str(e)}'}), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok'}), 200
