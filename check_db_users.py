import pymysql

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='multi_cancer_db'
    )
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, email, role, LEFT(password_hash, 50) as hash_preview FROM users")
    users = cursor.fetchall()
    
    print("=== USERS IN DATABASE ===\n")
    for user in users:
        print(f"ID: {user[0]}")
        print(f"Email: {user[1]}")
        print(f"Role: {user[2]}")
        print(f"Hash preview: {user[3]}")
        print("-" * 50)
    
    conn.close()
except Exception as e:
    print(f"Error: {e}")