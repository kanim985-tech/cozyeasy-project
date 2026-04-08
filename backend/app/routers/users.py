# from fastapi import APIRouter, HTTPException, Depends
# from fastapi.security import OAuth2PasswordRequestForm
# from app.database import get_db_connection
# from pydantic import BaseModel, EmailStr
# from passlib.context import CryptContext
# from datetime import datetime, timedelta
# from jose import jwt
# import uuid
# import os
# import logging

# router = APIRouter(prefix="/api/users", tags=["Authentication"])

# # 🔐 Security Config
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 60


# # 📦 Request Model
# class UserRegister(BaseModel):
#     username: str
#     email: EmailStr
#     password: str


# # 🔑 Create JWT Token
# def create_access_token(data: dict):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# # 📝 Register API
# @router.post("/register")
# def register_user(user: UserRegister):
#     conn = None
#     cursor = None
#     try:
#         # 🔒 Password validation
#         if len(user.password) < 8:
#             raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

#         if len(user.password.encode('utf-8')) > 72:
#             raise HTTPException(status_code=400, detail="Password too long")

#         conn = get_db_connection()
#         cursor = conn.cursor()

#         # 📧 Check existing email
#         cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
#         if cursor.fetchone():
#             raise HTTPException(status_code=400, detail="Email already registered")

#         # 🆔 Generate user ID
#         user_id_val = "USR-" + str(uuid.uuid4())[:8].upper()

#         # 🔐 Hash password
#         hashed_password = pwd_context.hash(user.password)

#         # 💾 Insert user
#         cursor.execute("""
#             INSERT INTO users (user_id, username, email, password, role)
#             VALUES (%s, %s, %s, %s, %s)
#         """, (user_id_val, user.username, user.email, hashed_password, 'customer'))

#         conn.commit()

#         return {
#             "message": "User registered successfully",
#             "user_id": user_id_val
#         }

#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         if conn:
#             conn.rollback()
#         logging.error(f"Register Error: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()


# # 🔐 Login API
# @router.post("/login")
# def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
#     conn = None
#     cursor = None
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()

#         # ⚠️ OAuth uses "username" field → we treat as email
#         email = form_data.username

#         cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
#         user = cursor.fetchone()

#         # ❌ Invalid credentials
#         if not user or not pwd_context.verify(form_data.password, user['password']):
#             raise HTTPException(status_code=401, detail="Invalid email or password")

#         # 🎟️ Generate token
#         token = create_access_token(
#             data={"sub": user['email'], "role": user['role']}
#         )

#         return {
#             "access_token": token,
#             "token_type": "bearer",
#             "role": user['role'],
#             "username": user['username'],
#             "user_id": user['user_id']
#         }

#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logging.error(f"Login Error: {e}")
#         raise HTTPException(status_code=500, detail="Internal Server Error")
#     finally:
#         if cursor:
#             cursor.close()
#         if conn:
#             conn.close()

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.database import get_db_connection
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import uuid
import os
import logging

router = APIRouter(prefix="/api/users", tags=["Authentication"])

# 🔐 Security Config
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


# ------------------ SCHEMAS ------------------

class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ------------------ JWT TOKEN ------------------

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ------------------ REGISTER ------------------

@router.post("/register")
def register_user(user: UserRegister):
    conn = None
    cursor = None
    try:
        # 🔒 Password validation
        if len(user.password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

        if len(user.password.encode('utf-8')) > 72:
            raise HTTPException(status_code=400, detail="Password too long")

        conn = get_db_connection()
        cursor = conn.cursor()

        # 📧 Check existing email
        cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

        # 🆔 Generate user_id
        user_id_val = "USR-" + str(uuid.uuid4())[:8].upper()

        # 🔐 Hash password
        hashed_password = pwd_context.hash(user.password)

        # 💾 Insert user
        cursor.execute("""
            INSERT INTO users (user_id, username, email, password, role)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id_val,
            user.username,
            user.email,
            hashed_password,
            "customer"
        ))

        conn.commit()

        return {
            "message": "User registered successfully",
            "user_id": user_id_val
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Register Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ------------------ LOGIN ------------------

@router.post("/login")
def login_user(user_data: UserLogin):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 🔍 Find user
        cursor.execute("SELECT * FROM users WHERE email = %s", (user_data.email,))
        user = cursor.fetchone()

        # ❌ Invalid credentials
        if not user or not pwd_context.verify(user_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # 🎟️ Generate JWT token
        token = create_access_token(
            data={
                "sub": user["email"],
                "role": user["role"],
                "user_id": user["user_id"]
            }
        )

        return {
            "message": "Login successful",
            "access_token": token,
            "token_type": "bearer",
            "role": user["role"],
            "username": user["username"],
            "user_id": user["user_id"]
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Login Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@router.get("/admin")
def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, user_id, username, email, role, created_at 
        FROM users
        ORDER BY id DESC
    """)

    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return users

@router.delete("/{user_id}")
def delete_user(user_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE user_id=%s", (user_id,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="User not found")

    cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "User deleted successfully"}