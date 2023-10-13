from fastapi import FastAPI, Depends, HTTPException, Form
from sqlalchemy.orm import Session

from fastapi.staticfiles import StaticFiles

import crud
import models
import schemas
from database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=f"User with id={user_id} not found")
    return db_user


@app.get("/passports", response_model=list[schemas.Passport])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_passports(db, skip=skip, limit=limit)
    return items


@app.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # totally possible for 2 people to share exact same name, birthday, place of birth
    db_user = crud.get_users_by_name(db,
                                     first_name=user.first_name, last_name=user.last_name, patronymic=user.patronymic)
    if db_user:
        pass    # Warning
    return crud.create_user(db=db, user=user)


@app.post("/users/{user_id}/passports/", response_model=schemas.Passport)
def create_passport_for_user(user_id: int, passport: schemas.PassportCreate, db: Session = Depends(get_db)):
    return crud.create_passport(db=db, passport=passport, user_id=user_id)


app.mount("/", StaticFiles(directory="public", html=True), name="static")
