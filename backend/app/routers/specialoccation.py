from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.database import get_db_connection

router = APIRouter(prefix="/api/SpecialOccasion", tags=["SpecialOccasion"])


# ✅ Request Model
class SpecialOccasionCreate(BaseModel):
    name: str = Field(..., min_length=1)
    caption: str = Field(..., min_length=1)
    image: str = Field(..., min_length=1)


# ✅ Response Model
class SpecialOccasionResponse(BaseModel):
    id: int
    name: str
    caption: str
    image: str


@router.post("/", response_model=dict)
def create_special_occasion(data: SpecialOccasionCreate):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO specialoccations (name, caption, image)
            VALUES (%s, %s, %s)
            """,
            (data.name, data.caption, data.image)
        )

        conn.commit()

        # ✅ Get last inserted ID (MySQL way)
        new_id = cursor.lastrowid

        return {
            "message": "Special Occasion created successfully",
            "id": new_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@router.get("/")
def get_special_occasions():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, caption, image FROM specialoccations")
        rows = cursor.fetchall()

        if not rows:
            return {"message": "No data found", "data": []}

        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]

        return result

    except Exception as e:
        print("ERROR:", e)  # 👈 check terminal for real error
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()