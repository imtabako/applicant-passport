from datetime import date

from pydantic import BaseModel


class PassportBase(BaseModel):
    doctype: str
    series: str
    number: str
    citizenship: str
    birthplace: str
    receipt_date: date
    division_code: str | None = None
    issued_by: str


class PassportCreate(PassportBase):
    pass


class Passport(PassportBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    first_name: str
    last_name: str
    patronymic: str
    sex: bool
    birthday: date
    comment: str | None = None


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    passports: list[Passport] = []

    class Config:
        orm_mode = True
