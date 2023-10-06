from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base


# Model cho bảng "Account"
class Account(Base):
    __tablename__ = "account"

    userID = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    time_create = Column(DateTime)
    time_update = Column(DateTime)
    status = Column(String)
    role = Column(String)

# Model cho bảng "Topic"
class Topic(Base):
    __tablename__ = "topic"

    TopicID = Column(Integer, primary_key=True, index=True)
    noidung = Column(String)
    anh = Column(String)
    userID = Column(Integer, ForeignKey("account.userID"))
    time_create = Column(DateTime)
    time_update = Column(DateTime)

    # Tạo mối quan hệ với bảng "Account"
    owner = relationship("Account", back_populates="topics")
    words = relationship("Word", back_populates="topic")

# Model cho bảng "Word"
class Word(Base):
    __tablename__ = "word"

    WordID = Column(Integer, primary_key=True, index=True)
    noidung = Column(String)
    anh = Column(String)
    userID = Column(Integer, ForeignKey("account.userID"))
    TopicID = Column(Integer, ForeignKey("topic.TopicID"))
    Time_create = Column(DateTime)
    Time_update = Column(DateTime)
    am_thanh = Column(String)

    # Tạo mối quan hệ với bảng "Account" và "Topic"
    owner = relationship("Account", back_populates="words")
    topic = relationship("Topic", back_populates="words")

# Tạo mối quan hệ ngược lại từ bảng "Account" đến các bảng liên quan
Account.topics = relationship("Topic", back_populates="owner")
Account.words = relationship("Word", back_populates="owner")
