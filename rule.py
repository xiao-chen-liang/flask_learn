from mysql.connector.abstracts import MySQLCursorAbstract

def add_college_and_grade_to_rule_table(info: dict, cursor: MySQLCursorAbstract):
    """Add college and grade to the rule table"""
    try:
        # Insert data into 'rule' table
        rule_query = "INSERT INTO rule (college, grade) VALUES (%s, %s)"
        rule_data = (info.get('college'), info['grade'])
        cursor.execute(rule_query, rule_data)
        print(f"Added the college and grade to the rule table: {info}")
        return True
    except Exception as e:
        error_message = f"An error occurred while adding college and grade to rule table: {e}"
        print(error_message)
        raise Exception(error_message)

# Judge whether the college and grade are in the table
def college_and_grade_is_exist(info: dict, cursor: MySQLCursorAbstract):
    """Decide whether the college and grade exist or not"""
    try:
        # Query the 'rule' table to check if the college and grade already exist
        cursor.execute("SELECT college, grade FROM rule WHERE college = %s AND grade = %s", (info.get('college'), info['grade']))
        result = cursor.fetchone()
        return True if result else False
    except Exception as e:
        error_message = f"An error occurred while checking college and grade in rule table: {e}"
        print(error_message)
        raise Exception(error_message)

# Example usage:
# conn = mysql_connection.connect_to_database()
# cursor = conn.cursor()
# try:
#     add_college_and_grade_to_rule_table(info, cursor)
# except Exception as e:
#     print(e)
# try:
#     college_and_grade_is_exist(info, cursor)
# except Exception as e:
#     print(e)
# cursor.close()
# conn.close()
def get_grades_and_colleges(cursor):
    """Get grades and colleges from the rule table"""
    try:
        # Query the 'rule' table to get all grades and colleges
        cursor.execute("SELECT college, grade FROM rule")
        result = cursor.fetchall()
        return result
    except Exception as e:
        error_message = f"An error occurred while getting grades and colleges from rule table: {e}"
        print(error_message)
        raise Exception(error_message)


def get_rule_data(grade, college, cursor):
    """Get rule data based on the selected grade and college"""
    try:
        # Query the 'rule' table to get the rule data based on grade and college
        cursor.execute("SELECT * FROM rule WHERE grade = %s AND college = %s", (grade, college))
        result = cursor.fetchone()
        if result:
            # Convert the fetched row to a dictionary
            columns = [desc[0] for desc in cursor.description]  # Get column names
            rule_dict = dict(zip(columns, result))  # Create dictionary from column names and row data
            return rule_dict
    except Exception as e:
        error_message = f"An error occurred while getting rule data: {e}"
        print(error_message)
        raise Exception(error_message)
    return None
