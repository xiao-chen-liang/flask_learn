from mysql.connector.abstracts import MySQLCursorAbstract

def add_collage_and_grade_to_rule_table(info: dict, cursor: MySQLCursorAbstract):
    """Add collage and grade to the rule table"""
    try:
        # Insert data into 'rule' table
        rule_query = "INSERT INTO rule (collage, grade) VALUES (%s, %s)"
        rule_data = (info.get('collage'), info['grade'])
        cursor.execute(rule_query, rule_data)
        print(f"Added the collage and grade to the rule table: {info}")
        return True
    except Exception as e:
        error_message = f"An error occurred while adding collage and grade to rule table: {e}"
        print(error_message)
        raise Exception(error_message)

# Judge whether the collage and grade are in the table
def collage_and_grade_is_exist(info: dict, cursor: MySQLCursorAbstract):
    """Decide whether the collage and grade exist or not"""
    try:
        # Query the 'rule' table to check if the collage and grade already exist
        cursor.execute("SELECT collage, grade FROM rule WHERE collage = %s AND grade = %s", (info.get('collage'), info['grade']))
        result = cursor.fetchone()
        return True if result else False
    except Exception as e:
        error_message = f"An error occurred while checking collage and grade in rule table: {e}"
        print(error_message)
        raise Exception(error_message)

# Example usage:
# conn = mysql_connection.connect_to_database()
# cursor = conn.cursor()
# try:
#     add_collage_and_grade_to_rule_table(info, cursor)
# except Exception as e:
#     print(e)
# try:
#     collage_and_grade_is_exist(info, cursor)
# except Exception as e:
#     print(e)
# cursor.close()
# conn.close()
