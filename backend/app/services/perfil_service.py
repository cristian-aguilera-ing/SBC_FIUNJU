# Este es el archivo: backend/app/services/perfil_service.py

from sqlalchemy.orm import Session
from app.models.perfil import UserMateria
from app.schemas.perfil import UserMateriaCreate

def get_materias_for_user(db: Session, user_id: int):
    """Obtiene todas las materias del perfil de un usuario."""
    return db.query(UserMateria).filter(UserMateria.user_id == user_id).all()

def add_materia_to_user(db: Session, user_id: int, materia: UserMateriaCreate):
    """Añade una nueva materia al perfil de un usuario."""
    
    # Opcional: Verifica si ya existe para no duplicarla
    db_materia = db.query(UserMateria).filter(
        UserMateria.user_id == user_id, 
        UserMateria.materia_uri == materia.materia_uri
    ).first()
    
    if db_materia:
        # Si ya existe, simplemente la actualiza
        db_materia.estado = materia.estado
    else:
        # Si no existe, la crea
        db_materia = UserMateria(
            **materia.model_dump(), 
            user_id=user_id
        )
        db.add(db_materia)
    
    db.commit()
    db.refresh(db_materia)
    return db_materia

def delete_materia_from_user(db: Session, user_id: int, user_materia_id: int) -> bool:
    """
    Elimina una materia del perfil de un usuario.
    Verifica que la materia pertenezca al usuario antes de borrarla.
    """
    db_materia = db.query(UserMateria).filter(
        UserMateria.id == user_materia_id,
        UserMateria.user_id == user_id
    ).first()
    
    if db_materia:
        db.delete(db_materia)
        db.commit()
        return True # Borrado exitoso
    
    return False # No se encontró la materia o no pertenecía al usuario