from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import get_db_connection
import pymysql

router = APIRouter(prefix="/api/contacts", tags=["Contacts"])


# ---------------- SCHEMA ----------------
class ContactCreate(BaseModel):
    fullname: str
    email: str
    subject: str
    message: str


# ---------------- CREATE ----------------
@router.post("/")
def create_contact(contact: ContactCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO contacts (fullname, email, subject, message)
            VALUES (%s, %s, %s, %s)
        """, (
            contact.fullname,
            contact.email,
            contact.subject,
            contact.message
        ))

        conn.commit()
        return {"message": "Message sent successfully"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()


# ---------------- GET ALL ----------------
@router.get("/")
def get_contacts():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT * FROM contacts ORDER BY id DESC")
    contacts = cursor.fetchall()

    cursor.close()
    conn.close()

    return contacts


# ---------------- DELETE ----------------
@router.delete("/{contact_id}")
def delete_contact(contact_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM contacts WHERE id = %s", (contact_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Contact not found")

        cursor.execute("DELETE FROM contacts WHERE id = %s", (contact_id,))
        conn.commit()

        return {"message": "Contact deleted successfully"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()