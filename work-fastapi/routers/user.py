from fastapi import APIRouter, Depends, Query,  Request, HTTPException, Path
from sqlalchemy.orm import Session
from db.database import SessionLocal
from crud import user as crud_user
from schemas import user as schema_user
from schemas.user import UserOut
from typing import List
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schema_user.UserOut)
def create_user(user: schema_user.UserCreate, db: Session = Depends(get_db)):
    return crud_user.create_user(db, user)

@router.get("/", response_model=List[UserOut])
def read_users(db: Session = Depends(get_db)):
    return crud_user.get_all_users(db)

@router.get("/search", response_model=List[UserOut])
def search_users(name: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    return crud_user.search_users_by_name(db, name_query=name)

@router.get("/form", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@router.get("/list-html", response_class=HTMLResponse)
async def user_list_page(request: Request):
    return templates.TemplateResponse("list.html", {"request": request})

@router.delete("/{user_id}")
def delete_user(user_id: int = Path(...), db: Session = Depends(get_db)):
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    crud_user.delete_user(db, user_id)
    return {"message": "Deleted"}

@router.patch("/{user_id}", response_model=schema_user.UserOut)
def update_user(user_id: int, update_data: schema_user.UserCreate, db: Session = Depends(get_db)):
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud_user.update_user(db, user_id, update_data)