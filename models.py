from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    patronymic = Column(String)     # opt
    sex = Column(Boolean, default=True)
    birthday = Column(Date)
    comment = Column(String)

    passports = relationship("Passport", back_populates="user")


class Passport(Base):
    __tablename__ = "passports"

    id = Column(Integer, primary_key=True, index=True)
    doctype = Column(String)
    series = Column(String)
    number = Column(String)
    citizenship = Column(String)
    receipt_date = Column(Date)
    division_code = Column(String)  # opt
    issued_by = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="passports")
