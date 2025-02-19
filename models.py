from sqlalchemy import Integer, String, Text, create_engine
from sqlalchemy.orm import Mapped, DeclarativeBase, mapped_column
import os

class Database(DeclarativeBase):
    pass

class User(Database):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    password: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(String(30))
    date: Mapped[str] = mapped_column(Text)

class Novel(Database):
    __tablename__ = "novels"

    novel_id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    user_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    image: Mapped[str] = mapped_column(Text)
    about: Mapped[str] = mapped_column(Text)

class Comment(Database):
    __tablename__ = "comments"

    comment_id: Mapped[int] = mapped_column(primary_key=True)
    novel_id: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str] = mapped_column(String(7000))

if not os.path.isfile("novel.db"):
    engine = create_engine("sqlite:///novel.db", echo=True)
    Database.metadata.create_all(engine)
