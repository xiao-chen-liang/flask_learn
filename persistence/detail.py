import mysql.connector

""" add detail message to the detail table """

def add_detail_message_to_detail_table(conn: mysql.connector.connection.MySQLConnection, detail: list):
    cursor = conn.cursor()

    # Iterate over the data and insert each line into the table
    for line in detail:
        cursor.execute("""
                    INSERT INTO detail (sn, course, type, grade, point, semester)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, line)

    conn.commit()
    cursor.close()
    print(f"Added the detail message to the detail table: {detail}")

    return True


