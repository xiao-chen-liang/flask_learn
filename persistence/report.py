import mysql.connector

""" add report message to the report table"""
def add_report_message_to_report_table(conn: mysql.connector.connection.MySQLConnection, info: dict):
    cursor = conn.cursor()

    # Insert data into 'report' table
    report_query = "INSERT INTO report (sn, college, major, grade, name, total, required, specialized, public, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    report_data = (info['sn'], info.get('collage'), info.get('major'), info['grade'], info['name'], info.get('total'),
                   info.get('required'), info.get('specialized'), info.get('public'), info.get('data'))
    cursor.execute(report_query, report_data)

    conn.commit()
    cursor.close()
    print(f"Added the report message to the report table: {info}")

    return True

