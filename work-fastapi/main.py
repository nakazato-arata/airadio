from fastapi import FastAPI
from routers import user, program
from db.database import engine
from db.models import user as user_model, program as program_model

user_model.Base.metadata.create_all(bind=engine)
program_model.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user.router, prefix="/users", tags=["users"])
app.include_router(program.router, prefix="/programs", tags=["programs"])
