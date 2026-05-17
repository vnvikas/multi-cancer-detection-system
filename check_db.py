import pymysql

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='123456',
        database='multi_cancer_db'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"✓ Database connected! Found {count} users") 
    
    cursor.execute("SELECT email, role FROM users")
    users = cursor.fetchall()
    for user in users:
        print(f"  - {user[0]} ({user[1]})")
    
    conn.close()
except Exception as e:
    print(f"✗ Error: {e}")