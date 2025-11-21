from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- Volvemos a la importación segura "legacy" ---
from sqlalchemy.ext.declarative import declarative_base
# --- FIN DE CAMBIOS ---

import os

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base() # Esta línea ahora funciona

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()