import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Severin.10",
        port = 3306,
        database="ntsa"
    )

    if db.is_connected():
        print("✅ Connection to NTSA database successful!")
    else:
        print("❌ Connection failed.")

except mysql.connector.Error as e:
    print("Error while connecting to MySQL:", e)
