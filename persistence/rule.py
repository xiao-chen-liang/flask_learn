import mysql.connector

""" add collage and grade to the rule table """
def add_collage_and_grade_to_rule_table(conn: mysql.connector.connection.MySQLConnection, info: dict):
    cursor = conn.cursor()

    # Insert data into 'rule' table
    rule_query = "INSERT INTO rule (collage, grade) VALUES (%s, %s)"
    rule_data = (info.get('collage'), info['grade'])
    cursor.execute(rule_query, rule_data)

    conn.commit()
    cursor.close()
    print(f"Added the collage and grade to the rule table: {info}")


    return True

