from mysql.connector.abstracts import MySQLCursorAbstract

def add_report_message_to_report_table(info: dict, cursor: MySQLCursorAbstract):
    """Add report message to the report table"""
    try:
        # Insert data into 'report' table
        report_query = "INSERT INTO report (sn, college, major, grade, name, total, required, specialized, public, date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        report_data = (info['sn'], info.get('college'), info.get('major'), info['grade'], info['name'], info.get('total'),
                       info.get('required'), info.get('specialized'), info.get('public'), info.get('date'))
        cursor.execute(report_query, report_data)
        print(f"Added the report message to the report table: {info}")
        return True
    except Exception as e:
        error_message = f"An error occurred while adding report message to report table: {e}"
        print(error_message)
        raise Exception(error_message)

def sn_is_exist(info: dict, cursor: MySQLCursorAbstract):
    """Decide whether the info[sn] exists or not"""
    try:
        # Query the 'report' table to check if the student number already exists
        cursor.execute("SELECT sn FROM report WHERE sn = %s", (info['sn'],))
        result = cursor.fetchone()
        return True if result else False
    except Exception as e:
        error_message = f"An error occurred while checking if sn exists in report table: {e}"
        print(error_message)
        raise Exception(error_message)

def query_date(info: dict, cursor: MySQLCursorAbstract):
    """Query the date according to the info[sn]"""
    try:
        # Query the 'report' table to get the date
        cursor.execute("SELECT date FROM report WHERE sn = %s", (info['sn'],))
        result = cursor.fetchone()
        return result[0] if result else None
    except Exception as e:
        error_message = f"An error occurred while querying date from report table: {e}"
        print(error_message)
        raise Exception(error_message)

def change_date(info: dict, cursor: MySQLCursorAbstract):
    """Change the date to the current date according to the info[sn]"""
    try:
        # Update the 'report' table with the new date
        cursor.execute("UPDATE report SET date = %s WHERE sn = %s", (info['date'], info['sn']))
        print(f"Changed the date to the current date: {info['date']}")
        return True
    except Exception as e:
        error_message = f"An error occurred while changing date in report table: {e}"
        print(error_message)
        raise Exception(error_message)
