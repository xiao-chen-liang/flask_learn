from werkzeug.datastructures import FileStorage
import pdfplumber
from openpyxl import Workbook
import os
import report as report
import rule as rule
import detail as detail
import re
import custom_exceptions as ce
import traceback
import mysql_connection

upload_directory = 'uploads'
score_report_directory = 'score_report'

conn = mysql_connection.connect_to_database()
same_cursor = conn.cursor()


def extract_info(text: str):
    # Split the multi-line string into lines and select the first 4 lines
    first_4_lines = text.splitlines()[:4]

    info = {}  # Dictionary to store extracted information

    for line in first_4_lines:
        if '学院' in line:
            info['college'] = line.split('学院: ')[1].split(' ')[0]
        if '专业' in line:
            info['major'] = line.split('专业: ')[1].split(' ')[0]
        if '班级' in line:
            info['grade'] = line.split('班级: ')[1].split(' ')[0]
        if '学号' in line:
            info['sn'] = line.split('学号: ')[1].split(' ')[0]
        if '姓名' in line:
            info['name'] = line.split('姓名: ')[1].split(' ')[0]

    # Split the multi-line string into lines and select the last 4 lines
    lines = text.splitlines()
    last_4_lines = lines[-4:]

    for line in last_4_lines:
        if '获得总学分' in line:
            info['total'] = float(line.split('获得总学分 ')[1].split(' ')[0])
            info['required'] = float(line.split('必修 ')[1].split(' ')[0])
            info['specialized'] = float(line.split('专业选修 ')[1].split(' ')[0])
            info['public'] = float(line.split('公共选修 ')[1].split(' ')[0])
        if '打印日期' in line:
            info['date'] = line.split('打印日期:')[1].split(' ')[0]

    # Use regular expression to find four continuous digits
    match = re.search(r'\d{4}', info['grade'])
    info['grade'] = int(match.group()) if match else None

    return info


def extract_data(data: list, info: dict):
    # Find the index of the string '毕业论文（设计）题目'
    index = None
    for i, sublist in enumerate(data):
        if '毕业论文(设计)题目' in sublist:
            index = i
            break

    # Cut out the list after the occurrence of the string
    if index is not None:
        data = data[:index]

    del data[0]

    new_data = []
    for row in data:
        new_row = [row[0], row[1], row[2], row[3], row[4], row[5]]
        new_data.append(new_row)

    for row in data:
        new_row = [row[6], row[7], row[8], row[9], row[10], row[11], row[12], row[13]]
        new_data.append(new_row)

    for row in data:
        new_row = [row[14], row[15], row[16], row[17], row[18], row[19]]
        new_data.append(new_row)

    cleaned_list = [[item for item in sublist if item is not None and item != ''] for sublist in new_data]

    last_score_index = None  # Initialize last_score_index before the loop

    for i, sublist in enumerate(cleaned_list):
        if '必修' in sublist or '选修' in sublist or '公修' in sublist:
            last_score_index = i

    if last_score_index is not None:
        new = cleaned_list[:last_score_index + 1]
    else:
        new = cleaned_list[:]  # If the condition is never satisfied, use the entire cleaned_list

    semester = None
    last_data = []
    for row in new:
        if len(row) == 1:
            semester = row[0]
        else:
            row.append(semester)
            last_data.append(row)

    # Create a workbook and select the active worksheet
    wb = Workbook()
    ws = wb.active
    detail_data = []

    # Write data to the worksheet
    for row_index, row_data in enumerate(last_data):
        row_data = [info['sn']] + row_data
        detail_data.append(row_data)
        for col_index, value in enumerate(row_data):
            ws.cell(row=row_index + 1, column=col_index + 1, value=value)

    # Save the workbook to a file
    wb.save("fact.xlsx")

    return detail_data


def handle_file(file: FileStorage):
    try:
        filename = file.filename
        upload_path = os.path.join(upload_directory, filename)

        file.save(upload_path)

        with pdfplumber.open(upload_path) as pdf:
            text = pdf.pages[0].extract_text()
            data = pdf.pages[0].extract_table()

        info = extract_info(text)

        # find weather the report need to be updated or not
        if report.sn_is_exist(info, same_cursor):
            print("The sn is existed")

            # query the date according to the info[sn]
            database_date = report.query_date(info, same_cursor)
            # formats of database_date and info[date] is something like '2024/04/12'
            # turn the string to date type
            current_date = database_date.split('/')
            info_date = info['date'].split('/')
            # compare the date
            if current_date < info_date:
                print("The report need to be updated")
                detail_data = extract_data(data, info)

                try:
                    cursor = conn.cursor()
                    # Call the delete_detail_message_from_detail_table function from detail.py
                    detail.delete_detail_message_from_detail_table(info, cursor)
                    # Call the add_detail_message_to_detail_table function from detail.py
                    detail.add_detail_message_to_detail_table(detail_data, cursor)
                    # Call the change_date function from report.py
                    report.change_date(info, cursor)
                    conn.commit()
                except Exception as e:
                    conn.rollback()
                    raise e
                else:
                    res = "The report is updated"
                finally:
                    cursor.close()



            else:
                raise ce.TheReportIsNotNewestError("The report is not the newest")

        else:
            detail_data = extract_data(data, info)

            try:
                cursor = conn.cursor()
                # Call the add_report_message_to_report_table function from report.py
                report.add_report_message_to_report_table(info, cursor)
                # Call the add_detail_message_to_detail_table function from detail.py
                detail.add_detail_message_to_detail_table(detail_data, cursor)
                # judge the college and grade is existed or not
                # if not existed, add the college and grade to the rule table
                if not rule.college_and_grade_is_exist(info, same_cursor):
                    rule.add_college_and_grade_to_rule_table(info, cursor)
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            else:
                res = "The report is updated"
            finally:
                cursor.close()

    except ce.TheReportIsNotNewestError as e:
        print(f"The report is not the newest")
        traceback.print_exc()
        raise Exception(f"The report is not the newest")

    except Exception as e:
        # delete the file
        os.remove(upload_path)
        traceback.print_exc()
        raise Exception(f"The file has some problem")
    else:
        # rename the file to info.sn.pdf and remove it to the score_report directory
        # if the file is existed in the score_report directory, it will be replaced
        score_report_path = os.path.join(score_report_directory, info['sn'] + '.pdf')
        if os.path.exists(score_report_path):
            os.remove(score_report_path)
        os.rename(upload_path, score_report_path)
        return res


def get_grades_and_colleges():
    cursor = conn.cursor()
    # Call the get_grades_and_colleges function from rule.py
    res = rule.get_grades_and_colleges(cursor)
    cursor.close()
    return convert_to_cascader_options(res)


def convert_to_cascader_options(data):
    cascader_options = []

    # Group data by grade
    grouped_data = {}
    for college, grade in data:
        if grade not in grouped_data:
            grouped_data[grade] = []
        grouped_data[grade].append(college)

    # Convert data into cascader options format
    for grade, colleges in grouped_data.items():
        grade_option = {'value': grade, 'label': str(grade), 'children': []}
        college_options = [{'value': college, 'label': college} for college in colleges]
        grade_option['children'] = college_options
        cascader_options.append(grade_option)

    return cascader_options

# Example usage
def get_rule_data(grade, college):
    try:
        # cursor = conn.cursor()
        # Call the get_rule_data function from rule.py
        res = rule.get_rule_data(grade, college, same_cursor)
        return res
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        traceback.print_exc()
        raise e

