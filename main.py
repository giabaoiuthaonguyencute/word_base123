import datetime
from fastapi import FastAPI, HTTPException, Depends, status,Path
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
from typing import Optional
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from typing import Annotated,List
from database import SessionLocal
from models import Account
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from datetime import timedelta
from models import Word,Topic
from datetime import datetime,timedelta

import models, database  # Sử dụng các tên module cụ thể (models và database) của bạn

app = FastAPI()

# Tạo một đối tượng CryptContext với bcrypt
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AccountCreate(BaseModel):
    username: str
    password: str

# Lớp Pydantic cho việc đọc thông tin tài khoản
class AccountRead(BaseModel):
    userID: int
    username: str
    status: str
    role: str
    time_create: str = "none"
    time_update: str = "none"

# Lớp Pydantic cho việc cập nhật thông tin tài khoản
class AccountUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    status: Optional[str] = None
    role: Optional[str] = None

# Lớp Pydantic cho token
class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

# tạo người dùng mới
@app.post("/accounts/", response_model=AccountRead)
async def create_account(account: AccountCreate, db: db_dependency):
    # Hash mật khẩu trước khi lưu vào cơ sở dữ liệu
    hashed_password = password_context.hash(account.password)
    
    # Tạo đối tượng Account và lưu vào cơ sở dữ liệu
    db_account = models.Account(username=account.username, password=account.password,status="active",role="low_user")
    db.add(db_account)
    db.commit()
    db.refresh(db_account)

    db_account.time_create = str(db_account.time_create)
    db_account.time_update = str(db_account.time_update)
    
    return db_account
# đọc thông tin tài khoản
@app.get("/accounts/{userID}", response_model=AccountRead)
async def read_account(userID: int, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.userID == userID).first()
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    
    # Chuyển đổi time_create và time_update thành chuỗi
    account.time_create = str(account.time_create)
    account.time_update = str(account.time_update)
    
    return account

SECRET_KEY = b'FL0OLA0JeIbdzsmXgH8d0x_tJ9R2wxeIsMD9uQLqyD4='
ALGORITHM = "HS256"

# Tạo mã thông báo từ tên người dùng
def create_token(username: str):
    payload = {"sub": username}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

# Endpoint đăng nhập và tạo mã thông báo
def get_user(db: db_dependency, username: str):
    user = db.query(Account).filter(Account.username == username).first()
    return user

def authenticate_user(db: db_dependency, username: str, password: str):
    user = get_user(db, username)
    if user is None or user.password != password:
        return None
    return user

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_token(user["username"])
    return {"access_token": access_token, "token_type": "bearer"}

# Hàm để tạo token
SECRET_KEY = "your-secret-key"
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # Token hết hạn sau 15 phút
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

# Định nghĩa endpoint để xác thực người dùng
@app.post("/login")
async def login(username: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    # Tạo mã thông báo (token) và gửi lại cho người dùng
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


class WordCreate(BaseModel):
    noidung: str
    anh: str
    userID: int
    TopicID: int
    Time_create: str
    Time_update: str
    am_thanh: str
    topic_name: str

class Message(BaseModel):
    message: str

# Endpoint để thêm từ
@app.post("/words/", response_model=dict)  # Sử dụng dict cho response_model
async def create_word(word: WordCreate, db: Session = Depends(get_db)):
    # Kiểm tra xem `userID` có tồn tại trong bảng `Account` không
    user = db.query(Account).filter(Account.userID == word.userID).first()
    if user is None:
        raise HTTPException(status_code=400, detail="userID không hợp lệ")
    
    # Kiểm tra xem `TopicID` có tồn tại trong bảng `Topic` không
    topic = db.query(Topic).filter(Topic.TopicID == word.TopicID).first()
    if topic is None:
        new_topic = Topic(noidung=word.TopicID)  # Sửa thành tạo chủ đề với TopicID
        db.add(new_topic)
        db.commit()
        db.refresh(new_topic)
        topic_id = new_topic.TopicID
    else:
        topic_id = topic.TopicID
    
    # Tạo giá trị thời gian hiện tại
    current_time = datetime.utcnow()
    
    # Tạo đối tượng Word từ dữ liệu đầu vào
    db_word = Word(
        noidung=word.noidung,
        anh=word.anh,
        userID=word.userID,
        TopicID=topic_id,  # Sửa thành topic_id
        Time_create=current_time,
        Time_update=current_time,  # Giá trị ban đầu cũng là thời gian hiện tại
        am_thanh=word.am_thanh
    )
    
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    
    # Trả về thông báo sau khi từ được thêm thành công
    return {"message": "Từ đã được thêm thành công."}

# Hàm để lấy danh sách từ dựa trên userID
def get_words_by_user_id(user_id: int, db: db_dependency):
    words = db.query(Word).filter(Word.userID == user_id).all()
    return words

# Endpoint để lấy danh sách từ dựa trên userID
@app.get("/words/{user_id}")
def get_user_words(user_id: int, db: Session = Depends(get_db)):
    words = get_words_by_user_id(user_id, db)
    if not words:
        raise HTTPException(status_code=404, detail="Không tìm thấy từ cho userID này")
    return words

# Pydantic model cho xác thực người dùng
class UserAuthenticate(BaseModel):
    username: str

def verify_password(plain_password, hashed_password):
    return password_context.verify(plain_password, hashed_password)

# Dependency để xác định người dùng hiện tại dựa trên tên tài khoản và mật khẩu
def get_current_user(auth_data: UserAuthenticate, db: db_dependency):
    user = db.query(Account).filter(Account.username == auth_data.username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

# Pydantic model cho từ
class UpdatedWord(BaseModel):
    WordID: int
    noidung: str
    anh: str
    am_thanh: str
# Endpoint để sửa từ (word)
@app.put("/words/{word_id}", response_model=UpdatedWord)
def update_word(word_id: int, word_update: UpdatedWord, db: Session = Depends(SessionLocal), current_user: Account = Depends(get_current_user)):
    # Kiểm tra xem từ có tồn tại trong cơ sở dữ liệu không
    word = db.query(Word).filter(Word.WordID == word_id).first()
    if word is None:
        raise HTTPException(status_code=404, detail="Word not found")
    
    # Kiểm tra xem từ có thuộc về người dùng hiện tại không
    if word.userID != current_user.userID:
        raise HTTPException(status_code=403, detail="You don't have permission to update this word")

    # Cập nhật thông tin từ
    word.noidung = word_update.noidung
    word.anh = word_update.anh
    word.am_thanh = word_update.am_thanh
    db.commit()
    db.refresh(word)

    # Trả về thông tin từ sau khi sửa
    updated_word = UpdatedWord(
        WordID=word.WordID,
        noidung=word.noidung,
        anh=word.anh,
        am_thanh=word.am_thanh
    )
    return updated_word

# Định nghĩa một endpoint để xóa từ dựa trên ID của từ
@app.delete("/words/{word_id}")
def delete_word(
    word_id: int = Path(..., title="ID của từ cần xóa", ge=1),
    db: Session = Depends(SessionLocal),
    current_user: Account = Depends(get_current_user)
):
    # Tìm từ theo ID
    word = db.query(Word).filter(Word.WordID == word_id).first()

    # Kiểm tra xem từ có tồn tại không
    if word is None:
        raise HTTPException(status_code=404, detail="Từ không tồn tại")

    # Kiểm tra xem người dùng có quyền xóa từ không
    if word.userID != current_user.userID:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xóa từ này")

    # Xóa từ khỏi cơ sở dữ liệu
    db.delete(word)
    db.commit()
    
    return {"message": "Từ đã được xóa thành công"}