from fastapi import APIRouter, Depends, Query,  Request, HTTPException, Path
from sqlalchemy.orm import Session
from db.database import SessionLocal
from crud import program as crud_program
from schemas import program as schema_program
from schemas.program import ProgramOut
from typing import List
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import date, time, datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schema_program.ProgramOut)
def create_program(program: schema_program.ProgramCreate, db: Session = Depends(get_db)):
    return crud_program.create_program(db, program)

@router.get("/", response_model=List[ProgramOut])
def read_programs(db: Session = Depends(get_db)):
    return crud_program.get_all_programs(db)

# @router.get("/search", response_model=List[ProgramOut])
# def search_programs(name: str = Query(..., min_length=1), db: Session = Depends(get_db)):
#     return schema_program.search_programs_by_name(db, name_query=name)

@router.get("/form", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("program_form.html", {"request": request})

# @router.get("/list", response_class=HTMLResponse)
# async def program_list_page(request: Request):
#     return templates.TemplateResponse("program_form_list.html", {"request": request})



@router.get("/list-html", response_class=HTMLResponse)
def list_programs(request: Request, db: Session = Depends(get_db)):
    programs = crud_program.get_all_programs(db)
    return templates.TemplateResponse("program_list.html", {"request": request, "programs": programs})

@router.delete("/{program_id}")
def delete_program(program_id: int = Path(...), db: Session = Depends(get_db)):
    program = crud_program.get_program(db, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="program not found")
    crud_program.delete_program(db, program_id)
    return {"message": "Deleted"}

@router.patch("/{program_id}", response_model=schema_program.ProgramOut)
def update_program(program_id: int, update_data: schema_program.ProgramCreate, db: Session = Depends(get_db)):
    program = crud_program.get_program(db, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="program not found")
    return crud_program.update_program(db, program_id, update_data)


@router.get("/test", response_model=List[ProgramOut])
async def program_test(request: Request, db: Session = Depends(get_db)):
    return  crud_program.test(db)

# 指定した日、時間でプログラムを検索する
@router.get("/search_by_datetime", response_model=List[ProgramOut])
def search_by_datetime(
    date_: date = Query(..., alias="date"),
    time_: time = Query(..., alias="time"),
    db: Session = Depends(get_db)
):
    return crud_program.search_program_by_datetime(db, target_date=date_, target_time=time_)