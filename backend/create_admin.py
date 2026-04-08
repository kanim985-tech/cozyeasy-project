from app.database import get_db_connection
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin():
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        email = "admin@gmail.com"

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            print("⚠️ Admin already exists!")
            return

        user_id = "ADMIN-" + str(uuid.uuid4())[:8].upper()

        password = "admin123"

        # 🔐 safe hashing
        hashed_password = pwd_context.hash(password.strip())

        cursor.execute("""
            INSERT INTO users (user_id, username, email, password, role)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            user_id,
            "Admin",
            email,
            hashed_password,
            "admin"
        ))

        conn.commit()

        print("✅ Admin created successfully!")

    except Exception as e:
        conn.rollback()
        print("❌ Error:", e)

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    create_admin()