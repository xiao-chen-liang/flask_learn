from mysql.connector.abstracts import MySQLCursorAbstract

def add_detail_message_to_detail_table(detail: list, cursor: MySQLCursorAbstract):
    """Add detail message to the detail table"""
    try:
        # Iterate over the data and insert each line into the table
        for line in detail:
            cursor.execute("""
                        INSERT INTO detail (sn, course, type, grade, point, semester)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, line)
        print(f"Added the detail message to the detail table: {detail}")
        return True
    except Exception as e:
        error_message = f"An error occurred while adding detail message to detail table: {e}"
        print(error_message)
        raise Exception(error_message)


# Delete record from the detail table according to info[sn]
def delete_detail_message_from_detail_table(info: dict, cursor: MySQLCursorAbstract):
    try:
        # Delete data from 'detail' table
        cursor.execute("DELETE FROM detail WHERE sn = %s", (info['sn'],))
        print(f"Deleted the detail message from the detail table: {info}")
        return True
    except Exception as e:
        error_message = f"An error occurred while deleting detail message from detail table: {e}"
        print(error_message)
        raise Exception(error_message)
