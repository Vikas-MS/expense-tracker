from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication and profile management."""
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Verify password."""
        return check_password_hash(self.password_hash, password)

    def get_total_income(self, start_date=None, end_date=None):
        """Get total income for user, optionally filtered by date range."""
        query = Transaction.query.filter_by(user_id=self.id, transaction_type='income')
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        return sum(t.amount for t in query.all()) or 0

    def get_total_expenses(self, start_date=None, end_date=None):
        """Get total expenses for user, optionally filtered by date range."""
        query = Transaction.query.filter_by(user_id=self.id, transaction_type='expense')
        if start_date:
            query = query.filter(Transaction.transaction_date >= start_date)
        if end_date:
            query = query.filter(Transaction.transaction_date <= end_date)
        return sum(t.amount for t in query.all()) or 0

    def get_balance(self):
        """Calculate current balance (total income - total expenses)."""
        return self.get_total_income() - self.get_total_expenses()

    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }


class Category(db.Model):
    """Category model for organizing transactions."""
    __tablename__ = 'categories'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    category_name = db.Column(db.String(100), nullable=False)
    category_type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    color = db.Column(db.String(7), default='#3498db')  # Hex color code
    is_custom = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    transactions = db.relationship('Transaction', backref='category', lazy=True, cascade='all, delete-orphan')

    __table_args__ = (db.UniqueConstraint('user_id', 'category_name', name='unique_user_category'),)

    def to_dict(self):
        """Convert category to dictionary."""
        return {
            'id': self.id,
            'category_name': self.category_name,
            'category_type': self.category_type,
            'color': self.color,
            'is_custom': self.is_custom
        }


class Transaction(db.Model):
    """Transaction model for income and expenses."""
    __tablename__ = 'transactions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    category_id = db.Column(db.String(36), db.ForeignKey('categories.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'income' or 'expense'
    description = db.Column(db.String(255))
    transaction_date = db.Column(db.Date, nullable=False, index=True, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert transaction to dictionary."""
        return {
            'id': self.id,
            'category_id': self.category_id,
            'category_name': self.category.category_name,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'description': self.description,
            'transaction_date': self.transaction_date.isoformat(),
            'created_at': self.created_at.isoformat()
        }
