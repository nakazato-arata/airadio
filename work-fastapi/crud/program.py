from sqlalchemy.orm import Session
from db.models.program import Program
from schemas.program import ProgramCreate
from datetime import date, time, datetime

def create_program(db: Session, program: ProgramCreate):
    db_program = Program(contents=program.contents, start_date=program.start_date, end_date=program.end_date, start_time=program.start_time, end_time=program.end_time)
    db.add(db_program)
    db.commit()
    db.refresh(db_program)
    return db_program

def get_all_programs(db: Session):
    return db.query(Program).all()

# def search_users_by_name(db: Session, name_query: str):
#     return db.query(User).filter(User.name.ilike(f"%{name_query}%")).all()

def get_program(db: Session, user_id: int):
    return db.query(Program).filter(Program.id == user_id).first()

def delete_program(db: Session, program_id: int):
    user = get_program(db, program_id)
    if user:
        db.delete(user)
        db.commit()

def update_program(db: Session, program_id: int, program_data: ProgramCreate):
    program = get_program(db, program_id)
    if program:
        program.name = program_data.contents
        program.start_date = program_data.start_date
        program.end_date = program_data.end_date
        program.start_time = program_data.start_time
        program.end_time = program_data.end_time
        db.commit()
        db.refresh(program)
        return program