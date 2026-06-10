from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
    func,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from db import Base, get_session


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, default=gen_uuid)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    categories = relationship('Category', backref='user', cascade='all, delete-orphan')
    transactions = relationship('Transaction', backref='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_total_income(self, start_date=None, end_date=None):
        session = get_session()
        try:
            q = session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
                Transaction.user_id == self.id,
                Transaction.transaction_type == 'income',
            )
            if start_date:
                q = q.filter(Transaction.transaction_date >= start_date)
            if end_date:
                q = q.filter(Transaction.transaction_date <= end_date)
            return float(q.scalar() or 0)
        finally:
            session.close()

    def get_total_expenses(self, start_date=None, end_date=None):
        session = get_session()
        try:
            q = session.query(func.coalesce(func.sum(Transaction.amount), 0)).filter(
                Transaction.user_id == self.id,
                Transaction.transaction_type == 'expense',
            )
            if start_date:
                q = q.filter(Transaction.transaction_date >= start_date)
            if end_date:
                q = q.filter(Transaction.transaction_date <= end_date)
            return float(q.scalar() or 0)
        finally:
            session.close()

    def get_balance(self):
        return self.get_total_income() - self.get_total_expenses()

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Category(Base):
    __tablename__ = 'categories'

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    category_name = Column(String(100), nullable=False)
    category_type = Column(String(20), nullable=False)
    color = Column(String(7), default='#3498db')
    is_custom = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    transactions = relationship('Transaction', backref='category', cascade='all, delete-orphan')

    __table_args__ = (UniqueConstraint('user_id', 'category_name', name='unique_user_category'),)

    def to_dict(self):
        return {
            'id': self.id,
            'category_name': self.category_name,
            'category_type': self.category_type,
            'color': self.color,
            'is_custom': self.is_custom,
        }


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(String(36), primary_key=True, default=gen_uuid)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey('categories.id'), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False)
    description = Column(String(255))
    transaction_date = Column(Date, nullable=False, index=True, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    bill_filename = Column(String(255))
    bill_original_name = Column(String(255))
    bill_mime_type = Column(String(100))
    bill_size = Column(Integer)

    @property
    def has_bill(self):
        return bool(self.bill_filename)

    def to_dict(self):
        return {
            'id': self.id,
            'category_id': self.category_id,
            'category_name': self.category.category_name if self.category else None,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'description': self.description,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'has_bill': self.has_bill,
            'bill_original_name': self.bill_original_name,
        }
