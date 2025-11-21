# Este es el archivo: backend/app/services/user_service.py

from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserPerfilUpdate 
from app.core.security import get_password_hash, verify_password


def get_user_by_email(db: Session, email: str) -> User | None:
    """Busca un usuario por su email."""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate) -> User:
    """Crea un nuevo usuario en la base de datos."""

    # --- CAMBIO ---
    # Ahora usa la función de security.py
    hashed_password = get_password_hash(user.password)
    # -------------

    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- NUEVA FUNCIÓN ---
def authenticate_user(db: Session, email: str, password: str) -> User | None:
    """
    Verifica si un usuario existe y si la contraseña es correcta.
    Devuelve el usuario si es exitoso, o None si falla.
    """
    user = get_user_by_email(db, email=email)

    # Si no encontramos el email o la contraseña no coincide
    if not user or not verify_password(password, user.hashed_password):
        return None

    # Si todo es correcto, devuelve el objeto User
    return user


def update_user_perfil(db: Session, user: User, perfil_data: UserPerfilUpdate) -> User:
    """
    Actualiza los campos del perfil personal de un usuario.
    """
    # Convierte el schema de Pydantic a un diccionario
    update_data = perfil_data.model_dump(exclude_unset=True)
    
    # Actualiza cada campo del objeto 'user' si venía en los datos
    for key, value in update_data.items():
        setattr(user, key, value)
        
    db.add(user)
    db.commit()
    db.refresh(user)
    return user