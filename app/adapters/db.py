from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlmodel import Session, create_engine
from app.utils.logger import log

from app.conf.config import get_app_settings

app_settings = get_app_settings()
#log(f'app settings: {app_settings}')
TM_ENGINE = create_engine(
    app_settings.tm_db_uri,
    pool_pre_ping=True,         # Checks if the connection is alive before using it
    # pool_recycle=3600,        # Reconnect after 1 hour (adjust as needed)
    pool_size=50, 
    max_overflow=60,
    pool_timeout=5              #  fail after 5s if no connection available
)

TM_SM_FACTORY: sessionmaker = sessionmaker(
    autocommit=False, autoflush=False, bind=TM_ENGINE
)

def get_toolmaster_db_connection() -> scoped_session:
    db = scoped_session(TM_SM_FACTORY)
    try:
        yield db
    finally:
        db.close()
