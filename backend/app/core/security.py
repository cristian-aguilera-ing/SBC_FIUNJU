# Este es el archivo: backend/app/core/security.py

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext

# --- Configuración de Passlib ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Configuración de JWT ---
# ¡MUY IMPORTANTE! Cambia esto por una cadena aleatoria y secreta
# Puedes generar una con: openssl rand -hex 32
SECRET_KEY = "tu-clave-secreta-super-dificil-de-adivinar" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # Token válido por 1 día

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña en texto plano contra un hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera un hash seguro para la contraseña."""
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    """Crea un nuevo Token de Acceso JWT."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict | None:
    """Decodifica un token para obtener sus datos (payload)."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        # Si el token es inválido o ha expirado
        return None
    
# --- NUEVA FUNCIÓN PARA PROTEGER ENDPOINTS ---
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.models.user import User
from app.services import user_service
from app.core.database import get_db

# Le dice a FastAPI "busca el token en la cabecera 'Authorization: Bearer <token>'"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Dependencia de FastAPI: Decodifica el token, extrae el email,
    y devuelve el objeto User de la base de datos.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str = payload.get("sub") # "sub" (subject) es el email
    if email is None:
        raise credentials_exception

    user = user_service.get_user_by_email(db, email=email)
    if user is None:
        # Si el usuario fue borrado de la BD pero el token aún es válido
        raise credentials_exception

    return user