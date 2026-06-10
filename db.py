from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

engine = None
Session = None
Base = declarative_base()


def init_app(app):
    """Initialize DB engine and session using app config."""
    global engine, Session
    database_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    if not database_uri:
        raise RuntimeError('Database URI not configured')

    engine = create_engine(database_uri, pool_pre_ping=True)
    Session = scoped_session(sessionmaker(bind=engine))


def get_session():
    if Session is None:
        raise RuntimeError('DB not initialized. Call init_app(app) first.')
    return Session()


def create_all():
    if engine is None:
        raise RuntimeError('DB not initialized. Call init_app(app) first.')
    # Ensure directory exists for SQLite file-based DBs
    try:
        db_path = engine.url.database
        if db_path and engine.url.drivername.startswith('sqlite'):
            import os
            parent = os.path.dirname(db_path)
            if parent and not os.path.exists(parent):
                os.makedirs(parent, exist_ok=True)
    except Exception:
        # best effort; continue to attempt create_all
        pass

    Base.metadata.create_all(bind=engine)
    migrate_schema()


def migrate_schema():
    """Add new columns to existing tables when the schema evolves."""
    if engine is None:
        return

    from sqlalchemy import inspect, text

    inspector = inspect(engine)
    if 'transactions' not in inspector.get_table_names():
        return

    columns = {col['name'] for col in inspector.get_columns('transactions')}
    new_columns = [
        ('bill_filename', 'VARCHAR(255)'),
        ('bill_original_name', 'VARCHAR(255)'),
        ('bill_mime_type', 'VARCHAR(100)'),
        ('bill_size', 'INTEGER'),
    ]

    with engine.begin() as conn:
        for col_name, col_type in new_columns:
            if col_name not in columns:
                conn.execute(text(f'ALTER TABLE transactions ADD COLUMN {col_name} {col_type}'))
