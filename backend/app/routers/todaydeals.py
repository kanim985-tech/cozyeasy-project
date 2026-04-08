from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import get_db_connection

router = APIRouter(prefix="/api/todaydeals", tags=["todaydeals"])

class Deals(BaseModel):
    offer_type: str
    image: str
    name: str
    caption: str

@router.post("/")
def create_todaydeals(deal: Deals):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO todaydeals (offer_type, image, name, caption)
            VALUES (%s, %s, %s, %s)
        """, (
            deal.offer_type,
            deal.image,
            deal.name,
            deal.caption
        ))

        conn.commit()
        return {"message": "Message sent successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@router.get("/")
def get_todaydeals():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM todaydeals")
    todaydeals = cursor.fetchall()

    cursor.close()
    conn.close()

    return todaydeals

@router.delete("/{deal_id}")
def delete_deals(deal_id:int):

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM todaydeals WHERE id = %s",(deal_id))
        if not cursor.fetchone():
            raise HTTPException (status_code=404, detail= "deal not found")
        cursor.execute("SELECT id FROM deal WHERE id = %s",(deal_id))

        conn.commit()
        return {"message":f"deal {deal_id} deleted successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException (status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


