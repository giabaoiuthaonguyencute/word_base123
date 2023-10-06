from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.orm import declarative_base
import datetime
from sqlalchemy.orm import declarative_base
import mysql.connector
DATABASE_URL = "mysql://root@127.0.0.1:3306/mydatabase"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Account(Base):
    __tablename__ = "account"

    userID = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    time_create = Column(DateTime, default=datetime.datetime.utcnow)
    time_update = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    status = Column(String)
    role = Column(String)

class Topic(Base):
    __tablename__ = "topic"

    TopicID = Column(Integer, primary_key=True, index=True)
    noidung = Column(String)
    anh = Column(String)
    userID = Column(Integer, ForeignKey("account.userID"))
    time_create = Column(DateTime, default=datetime.datetime.utcnow)
    time_update = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    owner = relationship("Account", back_populates="topics")

class Word(Base):
    __tablename__ = "word"

    WordID = Column(Integer, primary_key=True, index=True)
    noidung = Column(String)
    anh = Column(String)
    userID = Column(Integer, ForeignKey("account.userID"))
    TopicID = Column(Integer, ForeignKey("topic.TopicID"))
    Time_create = Column(DateTime, default=datetime.datetime.utcnow)
    Time_update = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    am_thanh = Column(String)

    owner = relationship("Account", back_populates="words")
    topic = relationship("Topic", back_populates="words")

Base.metadata.create_all(bind=engine)
