from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.database import get_db_connection
import uuid

router = APIRouter(prefix="/api/orders", tags=["Orders"])

# class OrderItem(BaseModel):
#     product_id: int
#     product_name: str
#     quantity: int
#     price: float
#     subtotal: float

# class OrderCreate(BaseModel):
#     user_id: str  
#     customer_name: str
#     phone: str
#     address: str
#     total_amount: float
#     payment_method: str
#     items: List[OrderItem]

# class StatusUpdate(BaseModel):
#     status: str


# @router.post("/")
# def create_order(order: OrderCreate):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     order_number = "ORD-" + uuid.uuid4().hex[:6].upper()

#     try:
#         # ✅ Insert order WITH order_number
#         query = """
#         INSERT INTO orders
#         (order_number, customer_name, phone, address, total_amount, payment_method, status, created_at)
#         VALUES (%s,%s,%s,%s,%s,%s,%s,NOW())
#         """
#         cursor.execute(query, (
#             order_number,
#             order.customer_name,
#             order.phone,
#             order.address,
#             order.total_amount,
#             order.payment_method,
#             "Pending"
#         ))

#         order_id = cursor.lastrowid

#         # Insert items
#         item_query = """
#         INSERT INTO order_item
#         (order_id, product_id, quantity, price, subtotal, created_at)
#         VALUES (%s,%s,%s,%s,%s,NOW())
#         """
#         for item in order.items:
#             cursor.execute(item_query, (
#                 order_id,
#                 item.product_id,
#                 item.quantity,
#                 item.price,
#                 item.subtotal
#             ))

#         conn.commit()

#         return {
#             "message": "Order placed successfully",
#             "order_number": order_number   # ✅ correct
#         }

#     except Exception as e:
#         conn.rollback()
#         raise HTTPException(status_code=400, detail=str(e))

#     finally:
#         cursor.close()
#         conn.close()


# # ✅ Use order_number instead of id
# @router.get("/{order_number}")
# def track_order(order_number: str):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)  # ✅ FIX

#     try:
#         cursor.execute("SELECT * FROM orders WHERE order_number=%s", (order_number,))
#         order = cursor.fetchone()

#         if not order:
#             raise HTTPException(status_code=404, detail="Order not found")

#         cursor.execute("SELECT * FROM order_item WHERE order_id=%s", (order["id"],))
#         items = cursor.fetchall()

#         order["items"] = items

#         return order

#     finally:
#         cursor.close()
#         conn.close()


# @router.get("/")
# def get_all_orders():
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)  # ✅ FIX

#     cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
#     orders = cursor.fetchall()

#     cursor.close()
#     conn.close()

#     return orders


# @router.put("/{order_number}")
# def update_status(order_number: str, data: StatusUpdate):
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     try:
#         cursor.execute(
#             "UPDATE orders SET status=%s WHERE order_number=%s",
#             (data.status, order_number)
#         )

#         conn.commit()

#         if cursor.rowcount == 0:
#             raise HTTPException(status_code=404, detail="Order not found")

#         return {"message": "Status updated successfully"}

#     except Exception as e:
#         conn.rollback()
#         raise HTTPException(status_code=400, detail=str(e))

#     finally:
#         cursor.close()
#         conn.close()

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.database import get_db_connection
import uuid
import pymysql

router = APIRouter(prefix="/api/orders", tags=["Orders"])


# ---------------- SCHEMAS ----------------
class OrderItem(BaseModel):
    product_id: int
    quantity: int
    price: float


class OrderCreate(BaseModel):
    user_id: str
    customer_name: str
    phone: str
    address: str
    city: str
    payment_method: str
    items: List[OrderItem]
    total_amount: float


# ---------------- CREATE ORDER ----------------
@router.post("/")
def create_order(order: OrderCreate):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        print("📦 ORDER RECEIVED:", order)   # 🔍 DEBUG

        # 🆔 generate order number
        order_number = "ORD-" + str(uuid.uuid4())[:8].upper()

        # ✅ insert into orders
        cursor.execute("""
            INSERT INTO orders 
            (order_number, user_id, customer_name, phone, address, city, total_amount, status, payment_method)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            order_number,
            order.user_id,
            order.customer_name,
            order.phone,
            order.address,
            order.city,
            order.total_amount,
            "Pending",
            order.payment_method
        ))

        order_id = cursor.lastrowid

        # ❌ SAFETY CHECK
        if not order.items or len(order.items) == 0:
            raise HTTPException(status_code=400, detail="No items in order")

        # ✅ insert order_items
        for item in order.items:
            print("🛒 ITEM:", item)

            # 🔍 check product exists
            cursor.execute("SELECT id FROM products WHERE id = %s", (item.product_id,))
            product = cursor.fetchone()

            if not product:
                raise HTTPException(
                    status_code=400,
                    detail=f"Product ID {item.product_id} not found"
                )

            subtotal = item.quantity * item.price

            cursor.execute("""
                INSERT INTO order_item 
                (order_id, product_id, quantity, price, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                order_id,
                item.product_id,
                item.quantity,
                item.price,
                subtotal
            ))
        conn.commit()

        return {
            "message": "Order placed successfully",
            "order_number": order_number
        }

    except Exception as e:
        conn.rollback()
        print("❌ ERROR:", e)   # 🔥 IMPORTANT DEBUG
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()


# ---------------- GET USER ORDERS ----------------
@router.get("/my-orders/{user_id}")
def get_user_orders(user_id: str):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute("""
            SELECT * FROM orders 
            WHERE user_id = %s 
            ORDER BY id DESC
        """, (user_id,))

        orders = cursor.fetchall()
        return orders

    except Exception as e:
        print("❌ ERROR FETCHING ORDERS:", e)
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()

# Admin side

@router.get("/admin")
def get_all_orders():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT * FROM orders 
        ORDER BY id DESC
    """)

    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return orders

class StatusUpdate(BaseModel):
    status: str


@router.put("/status/{order_id}")
def update_order_status(order_id: int, data: StatusUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE orders 
        SET status = %s 
        WHERE id = %s
    """, (data.status, order_id))

    conn.commit()

    cursor.close()
    conn.close()

    return {"message": "Status updated"}

@router.get("/{order_id}/items")
def get_order_items(order_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT oi.*, p.name 
        FROM order_item oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = %s
    """, (order_id,))

    items = cursor.fetchall()

    cursor.close()
    conn.close()

    return items

@router.get("/analytics")
def get_analytics():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        # total orders
        cursor.execute("SELECT COUNT(*) as total_orders FROM orders")
        total_orders = cursor.fetchone()["total_orders"]

        # total sales
        cursor.execute("SELECT SUM(total_amount) as total_sales FROM orders")
        total_sales = cursor.fetchone()["total_sales"] or 0

        # total customers ✅ FIX
        cursor.execute("SELECT COUNT(*) as total_customers FROM users")
        total_customers = cursor.fetchone()["total_customers"]

        # recent orders ✅ FIX
        cursor.execute("""
            SELECT order_number, status 
            FROM orders 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_orders = cursor.fetchall()

        # status chart
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM orders 
            GROUP BY status
        """)
        status_data = cursor.fetchall()

        # sales chart
        cursor.execute("""
            SELECT DATE(created_at) as date, SUM(total_amount) as total
            FROM orders
            GROUP BY DATE(created_at)
            ORDER BY date ASC
        """)
        sales_data = cursor.fetchall()

        return {
            "total_orders": total_orders,
            "total_sales": total_sales,
            "total_customers": total_customers,   # ✅ NEW
            "recent_orders": recent_orders,       # ✅ NEW
            "status_data": status_data,
            "sales_data": sales_data
        }

    finally:
        cursor.close()
        conn.close()