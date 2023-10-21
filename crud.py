from datetime import date

from sqlalchemy.orm import Session

import models
import schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_users_by_name(db: Session, first_name: str, last_name: str, patronymic: str):
    return (db.query(models.User)
            .filter(
        models.User.first_name == first_name,
        models.User.last_name == last_name,
        models.User.patronymic == patronymic)
            .all())


def get_user_by_schema(db: Session, user: schemas.UserBase):
    return (db.query(models.User)
            .filter(models.User.last_name == user.last_name,
                    models.User.first_name == user.first_name,
                    models.User.patronymic == user.patronymic,
                    models.User.sex == user.sex,
                    models.User.birthday == user.birthday,
                    models.User.comment == user.comment)
            .first())


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return (db.query(models.User)
            .offset(skip).limit(limit)
            .all())


def get_user_passports(db: Session, user_id: int):
    return (db.query(models.Passport)
            .filter(models.Passport.user_id == user_id)
            .all())


def get_passports(db: Session, skip: int = 0, limit: int = 100):
    return (db.query(models.Passport)
            .offset(skip).limit(limit)
            .all())


def get_passport_by_schema(db: Session, passport: schemas.Passport):
    return (db.query(models.Passport)
            .filter(models.Passport.series == passport.series,
                    models.Passport.number == passport.number,
                    models.Passport.citizenship == passport.citizenship,
                    models.Passport.birthplace == passport.birthplace,
                    models.Passport.receipt_date == passport.receipt_date,
                    models.Passport.division_code == passport.division_code,
                    models.Passport.issued_by == passport.issued_by)
            .all())


def get_passport_by_series_number(db: Session, user_id: int, series: str, number: str):
    return (db.query(models.Passport)
            .filter(models.Passport.user_id == user_id, models.Passport.series == series,
                    models.Passport.number == number)
            .first())


def create_passport(db: Session, user_id: int, passport: schemas.PassportCreate):
    db_passport = models.Passport(**passport.dict(), user_id=user_id)
    db.add(db_passport)
    db.commit()
    db.refresh(db_passport)
    return db_passport


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

#
#
# last_name: str,
# first_name: str,
# patronymic: str,
# sex: bool,
# birthday: date,
# citizenship: str,
# birthplace: str,
# doctype: str,
# series: str,
# number: str,
# receipt_date: str,
# division_code: str,
# issued_by: str,
# comment: str,
