from sqlalchemy.orm import Session
from db.models.user import User
from schemas.user import UserCreate

def create_user(db: Session, user: UserCreate):
    db_user = User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_all_users(db: Session):
    return db.query(User).all()

def search_users_by_name(db: Session, name_query: str):
    return db.query(User).filter(User.name.ilike(f"%{name_query}%")).all()

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    if user:
        db.delete(user)
        db.commit()

def update_user(db: Session, user_id: int, user_data: UserCreate):
    user = get_user(db, user_id)
    if user:
        user.name = user_data.name
        db.commit()
        db.refresh(user)
        return user