import pymysql

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="kanimysql",
        database="cozyeasy", 
        cursorclass=pymysql.cursors.DictCursor
    )