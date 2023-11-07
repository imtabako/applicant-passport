import shutil
from datetime import date
from datetime import datetime
from random import random
from typing import Annotated
import hashlib
import os

import aiofiles
from fastapi import FastAPI, Depends, HTTPException, Form, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import crud
import models
import schemas

from database import SessionLocal, engine

BUFFER_SIZE = 1 << 16   # buffer size for reading UploadFile
FILE_SIZE_MAX = 1 << 21 # 2 MiB

image_dir = os.path.join(os.getcwd(), 'static/images')
if not os.path.exists(image_dir):
    os.mkdir(image_dir)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")


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


# index.html
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# find/create user and passport
#  returns:
#  0 -- found user and passport
#  +1 -- created user
#  +2 -- created passport
@app.post("/postdata")
async def handle_post(
        file: UploadFile = File(),
        last_name: str = Form(...),
        first_name: str = Form(...),
        patronymic: str = Form(None),
        sex: str = Form(...),
        birthday: str = Form(...),
        citizenship: str = Form(...),
        birthplace: str = Form(...),
        doctype: str = Form(...),
        series: str = Form(...),
        number: str = Form(...),
        receipt_date: str = Form(...),
        division_code: str = Form(None),
        issued_by: str = Form(...),
        comment: str = Form(None),
        db: Session = Depends(get_db)
):
    print(sex)
    print(birthday)
    print(receipt_date)
    # return code
    result = 0

    print('FILE')
    print(file.filename)
    print(file.size)
    print(file.content_type)
    print(file is None)

    print('OPT')
    print(patronymic)
    print(division_code)
    print(comment)

    # validate `sex', `birthday', `receipt_date' and re-type to Bool, Date, Date
    sex = sex == 'm'
    birthday = datetime.strptime(birthday, '%Y-%m-%d').date()
    receipt_date = datetime.strptime(receipt_date, '%Y-%m-%d').date()

    # file validation
    if file.size > 0:
        if file.size > FILE_SIZE_MAX:
            raise HTTPException(status_code=400, detail='File size too large')

        if file.content_type not in ['image/jpeg', 'image/png']:
            raise HTTPException(status_code=400, detail='Invalid file type')
    else:
        print('NO FILE')

    # user required schema fields
    user_fields = {"first_name": first_name, "last_name": last_name, "patronymic": patronymic, "sex": sex,
                   "birthday": birthday, "comment": comment}

    # photo
    if file.size > 0:
        print(file)
        print(file.filename)
        print(file.size)  # in bytes
        # basename = await calculate_sha1(file)
        # filename = f"{image_dir}/{db_user.id}.{extension}"
        userid = int(random() * 100) % 20
        extension = file.filename.split('.')[-1]
        filename = f"{image_dir}/{userid}.{extension}"
        print(filename)
        if os.path.isfile(filename):
            print(f"Warning: {filename} already exists, rewriting")

        with open(filename, 'wb') as buf:
            shutil.copyfileobj(file.file, buf)
        user_fields["photo_path"] = filename

    user = schemas.UserCreate(**user_fields)
    passport = schemas.PassportCreate(doctype=doctype, series=series, number=number, citizenship=citizenship,
                                      birthplace=birthplace, receipt_date=receipt_date, division_code=division_code,
                                      issued_by=issued_by)

    print(user_fields)
    print(user)
    print(passport)

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


# TODO: OK
# return all users
@app.get("/users", response_model=list[schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


# TODO: OK
# return a user
@app.get("/users/{user_id}", response_model=schemas.User)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail=f"User with id={user_id} not found")
    return db_user


# TODO: OK
# return all passports
@app.get("/passports", response_model=list[schemas.Passport])
async def read_passports(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_passports(db, skip=skip, limit=limit)
    return items
