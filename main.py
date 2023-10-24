import shutil
from datetime import date
from datetime import datetime
from typing import Annotated
import hashlib
import os

import aiofiles
from fastapi import FastAPI, Depends, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from fastapi.staticfiles import StaticFiles

import crud
import models
import schemas

from database import SessionLocal, engine

BUFFER_SIZE = 1 << 16   # buffer size for reading UploadFile
FILE_SIZE_MAX = 1 << 21 # 2 MiB

image_dir = os.path.join(os.getcwd(), './public/images')
if not os.path.exists(image_dir):
    os.mkdir(image_dir)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# calculate file hash, returns {filename hash}-{file hash}.{extension}
async def calculate_sha1(file):
    # filename
    hasher = hashlib.md5()
    hasher.update(str.encode(file.filename))
    filename_hash = hasher.hexdigest()

    # file content
    hasher = hashlib.sha1()
    while fb := await file.read(BUFFER_SIZE):
        hasher.update(fb)

    await file.seek(0)
    return f"{filename_hash[:4]}-{hasher.hexdigest()[:6]}.{file.filename.split('.')[-1]}"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# find/create user and passport
#  returns:
#  0 -- found user and passport
#  +1 -- created user
#  +2 -- created passport
@app.post("/postdata")
async def handle_post(
        file: UploadFile = File(...),
        last_name: str = Form(...),
        first_name: str = Form(...),
        patronymic: str = Form(...),
        sex: str = Form(...),
        birthday: str = Form(...),
        citizenship: str = Form(...),
        birthplace: str = Form(...),
        doctype: str = Form(...),
        series: str = Form(...),
        number: str = Form(...),
        receipt_date: str = Form(...),
        division_code: str = Form(...),
        issued_by: str = Form(...),
        comment: str = Form(...),
        db: Session = Depends(get_db)
):
    print(sex)
    print(birthday)
    print(receipt_date)
    # return code
    result = 0

    # re-type to Bool, Date, Date
    sex = sex == 'm'
    birthday = datetime.strptime(birthday, '%Y-%m-%d').date()
    receipt_date = datetime.strptime(receipt_date, '%Y-%m-%d').date()

    # file validation
    if file.size > FILE_SIZE_MAX:
        raise HTTPException(status_code=400, detail='File size too large')

    if file.content_type not in ['image/jpeg', 'image/png']:
        raise HTTPException(status_code=400, detail='Invalid file type')

    user = schemas.UserCreate(first_name=first_name, last_name=last_name, patronymic=patronymic,
                              sex=sex, birthday=birthday, comment=comment)
    passport = schemas.PassportCreate(doctype=doctype, series=series, number=number, citizenship=citizenship,
                                      birthplace=birthplace, receipt_date=receipt_date, division_code=division_code,
                                      issued_by=issued_by)

    # find or create user entity
    db_user = crud.get_user_by_schema(db, user)
    if db_user is None:
        db_user = crud.create_user(db, user)
        user_dir = f"{image_dir}/{db_user.id}"
        os.mkdir(user_dir)
        result += 1
    print(db_user.id)

    # find or create passport entity
    db_passport = crud.get_passport_by_series_number(db, db_user.id, passport.series, number)
    if db_passport is None:
        db_passport = crud.create_passport(db, db_user.id, passport)
        result += 2

    # handle file upload
    print(file)
    print(file.filename)
    print(file.size)  # in bytes
    basename = await calculate_sha1(file)
    filename = f"{image_dir}/{db_user.id}/{basename}"
    print(filename)
    if os.path.isfile(filename):
        print(f"Warning: {filename} already exists, rewriting")

    with open(filename, 'wb') as buf:
        shutil.copyfileobj(file.file, buf)

    # async with aiofiles.open(filename, 'wb') as out:  # writing bytes
    #     while fb := await file.read(BUFFER_SIZE):
    #         await out.write(fb)

    # content.
    # print(content)

    # TODO: should return user & passport models, index.html should be (jinja) template
    return {"result": result}


# return all users' info
@app.get("/users", response_model=list[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


# return user info
@app.get("/users/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=f"User with id={user_id} not found")
    return db_user


# return user's passports
@app.get("/users/{user_id}/passports", response_model=list[schemas.Passport])
async def read_user_passports(user_id: int, db: Session = Depends(get_db)):
    return crud.get_user_passports(db, user_id=user_id)


# return all passports
@app.get("/passports", response_model=list[schemas.Passport])
async def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_passports(db, skip=skip, limit=limit)
    return items


# rudimentary function
@app.post("/users", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # totally possible for 2 people to share exact same name, birthday, place of birth
    db_user = crud.get_users_by_name(db,
                                     first_name=user.first_name, last_name=user.last_name, patronymic=user.patronymic)
    if db_user:
        pass  # Warning
    return crud.create_user(db=db, user=user)


app.mount("/", StaticFiles(directory="public", html=True), name="static")
