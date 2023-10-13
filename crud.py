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


def get_passport_by_number(db: Session, series: str, number: str):
    return (db.query(models.Passport)
            .filter(models.Passport.series == series, models.Passport.number == number)
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
