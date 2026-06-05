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
