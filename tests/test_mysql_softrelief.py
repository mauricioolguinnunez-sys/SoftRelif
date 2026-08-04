import mysql.connector

try:
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="07032007mon"
    )

    if conexion.is_connected():
        print("Conexión correcta a MySQL")

    cursor = conexion.cursor()
    cursor.execute("SHOW DATABASES;")

    for db in cursor.fetchall():
        print(db[0])

except mysql.connector.Error as error:
    print("Error:", error)

finally:
    if "cursor" in locals():
        cursor.close()

    if "conexion" in locals() and conexion.is_connected():
        conexion.close()