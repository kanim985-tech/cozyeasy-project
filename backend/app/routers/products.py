# from fastapi import APIRouter, HTTPException, Query
# from pydantic import BaseModel
# from typing import Optional, List
# from app.database import get_db_connection
# import pymysql.cursors

# router = APIRouter(prefix="/api/products", tags=["products"])

# # ------------------ SCHEMA ------------------

# class ProductBase(BaseModel):
#     name: str
#     image: str
#     rating: float
#     price: float
#     old_price: Optional[float] = None
#     offer: Optional[int] = 0
#     description: str
#     quantity: int
#     category_id: int   # ✅ changed
#     category: Optional[str] = None   # ✅ ADD THIS
#     category_name: Optional[str] = None

# class ProductCreate(ProductBase):
#     pass

# class Product(ProductBase):
#     id: int
#     category_name: Optional[str] = None   # ✅ extra for JOIN


# # ------------------ CREATE ------------------

# @router.post("/", response_model=Product)
# def create_product(product: ProductCreate):
#     conn = get_db_connection()
#     cursor = conn.cursor(pymysql.cursors.DictCursor)

#     query = """
#     INSERT INTO products 
#     (name, image, rating, price, old_price, offer, description, quantity, category_id)
#     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#     """

#     cursor.execute(query, (
#         product.name,
#         product.image,
#         product.rating,
#         product.price,
#         product.old_price,
#         product.offer,
#         product.description,
#         product.quantity,
#         product.category_id   # ✅ changed
#     ))

#     conn.commit()
#     product_id = cursor.lastrowid

#     cursor.close()
#     conn.close()

#     return {**product.dict(), "id": product_id}


# # ------------------ READ ALL ------------------

# @router.get("/", response_model=List[Product])
# def get_products(category: Optional[str] = Query(None)):
#     conn = get_db_connection()
#     cursor = conn.cursor(pymysql.cursors.DictCursor)

#     if category:
#         query = """
#         SELECT p.*, c.name AS category_name
#         FROM products p
#         JOIN categories c ON p.category_id = c.id
#         WHERE c.name = %s
#         """
#         cursor.execute(query, (category,))
#     else:
#         query = """
#         SELECT p.*, c.name AS category_name
#         FROM products p
#         JOIN categories c ON p.category_id = c.id
#         """
#         cursor.execute(query)

#     rows = cursor.fetchall()

#     cursor.close()
#     conn.close()

#     # convert category_name → category
#     for row in rows:
#         row["category"] = row["category_name"]

#     return rows


# # ------------------ READ ONE ------------------

# @router.get("/{product_id}", response_model=Product)
# def get_product(product_id: int):
#     conn = get_db_connection()
#     cursor = conn.cursor(pymysql.cursors.DictCursor)

#     query = """
#     SELECT p.*, c.name AS category_name
#     FROM products p
#     JOIN categories c ON p.category_id = c.id
#     WHERE p.id = %s
#     """

#     cursor.execute(query, (product_id,))
#     row = cursor.fetchone()

#     cursor.close()
#     conn.close()

#     if not row:
#         raise HTTPException(status_code=404, detail="Product not found")

#     return row


# # ------------------ UPDATE ------------------

# @router.put("/{product_id}", response_model=Product)
# def update_product(product_id: int, product: ProductCreate):
#     conn = get_db_connection()
#     cursor = conn.cursor(pymysql.cursors.DictCursor)

#     cursor.execute("SELECT id FROM products WHERE id=%s", (product_id,))
#     if not cursor.fetchone():
#         cursor.close()
#         conn.close()
#         raise HTTPException(status_code=404, detail="Product not found")

#     query = """
#     UPDATE products
#     SET name=%s, image=%s, rating=%s, price=%s, old_price=%s,
#         offer=%s, description=%s, quantity=%s, category_id=%s
#     WHERE id=%s
#     """

#     cursor.execute(query, (
#         product.name,
#         product.image,
#         product.rating,
#         product.price,
#         product.old_price,
#         product.offer,
#         product.description,
#         product.quantity,
#         product.category_id,   # ✅ changed
#         product_id
#     ))

#     conn.commit()

#     cursor.close()
#     conn.close()

#     return {**product.dict(), "id": product_id}


# # ------------------ DELETE ------------------

# @router.delete("/{product_id}")
# def delete_product(product_id: int):
#     conn = get_db_connection()
#     cursor = conn.cursor(pymysql.cursors.DictCursor)

#     cursor.execute("SELECT id FROM products WHERE id=%s", (product_id,))
#     if not cursor.fetchone():
#         cursor.close()
#         conn.close()
#         raise HTTPException(status_code=404, detail="Product not found")

#     cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
#     conn.commit()

#     cursor.close()
#     conn.close()

#     return {"message": "Product deleted successfully"}


# # ------------------ CATEGORIES API ------------------

# @router.get("/categories")
# def get_categories():
#     conn = get_db_connection()
#     cursor = conn.cursor(pymysql.cursors.DictCursor)

#     cursor.execute("SELECT id, name FROM categories")
#     rows = cursor.fetchall()

#     cursor.close()
#     conn.close()

#     return rows

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from app.database import get_db_connection
import pymysql.cursors

router = APIRouter(prefix="/api/products", tags=["products"])


# ------------------ SCHEMA ------------------

class ProductBase(BaseModel):
    name: str
    image: str
    rating: float
    price: float
    old_price: Optional[float] = None
    offer: Optional[int] = 0
    description: str
    quantity: int
    category_id: int
    category: Optional[str] = None
    category_name: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    category_name: Optional[str] = None


# ------------------ CATEGORIES (🔥 MOVE THIS UP) ------------------

@router.get("/categories")
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT id, name FROM categories")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows


# ------------------ CREATE ------------------

@router.post("/", response_model=Product)
def create_product(product: ProductCreate):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    query = """
    INSERT INTO products 
    (name, image, rating, price, old_price, offer, description, quantity, category_id)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        product.name,
        product.image,
        product.rating,
        product.price,
        product.old_price,
        product.offer,
        product.description,
        product.quantity,
        product.category_id
    ))

    conn.commit()
    product_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return {**product.dict(), "id": product_id}


# ------------------ READ ALL ------------------

@router.get("/", response_model=List[Product])
def get_products(category: Optional[str] = Query(None)):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if category:
        query = """
        SELECT p.*, c.name AS category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        WHERE c.name = %s
        """
        cursor.execute(query, (category,))
    else:
        query = """
        SELECT p.*, c.name AS category_name
        FROM products p
        JOIN categories c ON p.category_id = c.id
        """
        cursor.execute(query)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    for row in rows:
        row["category"] = row["category_name"]

    return rows


# ------------------ READ ONE ------------------

@router.get("/{product_id}", response_model=Product)
def get_product(product_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    query = """
    SELECT p.*, c.name AS category_name
    FROM products p
    JOIN categories c ON p.category_id = c.id
    WHERE p.id = %s
    """

    cursor.execute(query, (product_id,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Product not found")

    row["category"] = row["category_name"]

    return row


# ------------------ UPDATE ------------------

@router.put("/{product_id}", response_model=Product)
def update_product(product_id: int, product: ProductCreate):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT id FROM products WHERE id=%s", (product_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")

    query = """
    UPDATE products
    SET name=%s, image=%s, rating=%s, price=%s, old_price=%s,
        offer=%s, description=%s, quantity=%s, category_id=%s
    WHERE id=%s
    """

    cursor.execute(query, (
        product.name,
        product.image,
        product.rating,
        product.price,
        product.old_price,
        product.offer,
        product.description,
        product.quantity,
        product.category_id,
        product_id
    ))

    conn.commit()

    cursor.close()
    conn.close()

    return {**product.dict(), "id": product_id}


# ------------------ DELETE ------------------

@router.delete("/{product_id}")
def delete_product(product_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("SELECT id FROM products WHERE id=%s", (product_id,))
    if not cursor.fetchone():
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")

    cursor.execute("DELETE FROM products WHERE id=%s", (product_id,))
    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Product deleted successfully"}