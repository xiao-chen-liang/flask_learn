from werkzeug.datastructures import FileStorage
import pdfplumber
from openpyxl import Workbook
import os
import report as report
import rule as rule
import detail as detail
import allocation as allocation
import re
import custom_exceptions as ce
import traceback
import mysql_connection
from decimal import Decimal

upload_directory = 'uploads'
score_report_directory = 'score_report'


def extract_info(text: str):
    """extract information from the text of the first page of the report"""
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
    """extract data from the table of the report"""
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
    #     for col_index, value in enumerate(row_data):
    #         ws.cell(row=row_index + 1, column=col_index + 1, value=value)
    #
    # # Save the workbook to a file
    # wb.save("fact.xlsx")

    if not check_all_pass(detail_data):

        # find weather the report need to be updated or not
        if sn_is_exist(info):
            print("The sn is existed")

            # query the date according to the info[sn]
            database_date = query_date(info)
            # formats of database_date and info[date] is something like '2024/04/12'
            # turn the string to date type
            current_date = database_date.split('/')
            info_date = info['date'].split('/')
            # compare the date
            if current_date < info_date:
                print("The report is the newest, so the preview report need to be delete")
                with mysql_connection.connect_to_database() as conn:
                    with conn.cursor() as cursor:
                        detail.delete_detail_message_from_detail_table(info, cursor)
                        report.delete_report_message_from_report_table(info['sn'], cursor)
                        conn.commit()
                        raise ce.NotAllCoursesPassedError("Not all courses are passed, and the report is the newest, "
                                                          "so the preview report need to be delete")
            else:
                raise ce.NotAllCoursesPassedError("Not all courses are passed, but the report is not the newest, "
                                                  "so the preview report are reserved")
        else:
            raise ce.NotAllCoursesPassedError("Not all courses are passed, the report is discarded")

    return detail_data


def query_date(info):
    """query the date the report is generated according to the info[sn] in the report table"""
    with mysql_connection.connect_to_database() as conn:
        with conn.cursor() as cursor:
            return report.query_date(info, cursor)


def sn_is_exist(info):
    """decide whether the info[sn] exists or not in the report table"""
    with mysql_connection.connect_to_database() as conn:
        with conn.cursor() as cursor:
            return report.sn_is_exist(info, cursor)


def update_report(info, detail_data):
    """when the sn is existed, update the report and the detail table according to the info and detail_data"""
    with mysql_connection.connect_to_database() as conn:
        try:
            cursor = conn.cursor()
            # Call the delete_detail_message_from_detail_table function from detail.py
            detail.delete_detail_message_from_detail_table(info, cursor)
            # Call the add_detail_message_to_detail_table function from detail.py
            detail.add_detail_message_to_detail_table(detail_data, cursor)
            # Call the change_date function from report.py
            report.change_date(info, cursor)
        except Exception as e:
            conn.rollback()
            raise e
        else:
            res = "The report is updated"
            conn.commit()
            return res
        finally:
            cursor.close()


def upload_report(info, detail_data):
    """when the sn is not existed, add the report and the detail table according to the info and detail_data"""
    with mysql_connection.connect_to_database() as conn:
        try:
            cursor = conn.cursor()
            # Call the add_report_message_to_report_table function from report.py
            report.add_report_message_to_report_table(info, cursor)
            # Call the add_detail_message_to_detail_table function from detail.py
            detail.add_detail_message_to_detail_table(detail_data, cursor)
            # judge the college and grade is existed or not
            # if not existed, add the college and grade to the rule table
            if not rule.college_and_grade_is_exist(info, cursor):
                rule.add_college_and_grade_to_rule_table(info, cursor)
            # judge the major, college and grade is existed or not
            # if not existed, add the major, college and grade to the allocation table
            if not allocation.major_college_and_grade_is_exist(info, cursor):
                allocation.add_major_college_and_grade_to_allocation_table(info, cursor)

        except Exception as e:
            conn.rollback()
            raise e
        else:
            res = "The report is uploaded"
            conn.commit()
        finally:
            cursor.close()

    try:
        update_required_score_and_sum_of_sn(info)
    except Exception as e:
        raise e

    return res


def handle_file(file: FileStorage):
    """Handle the uploaded file and extract the required information"""
    try:
        filename = file.filename
        upload_path = os.path.join(upload_directory, filename)

        file.save(upload_path)

        with pdfplumber.open(upload_path) as pdf:
            text = pdf.pages[0].extract_text()
            data = pdf.pages[0].extract_table()

        info = extract_info(text)

        # find weather the report need to be updated or not
        if sn_is_exist(info):
            print("The sn is existed")

            # query the date according to the info[sn]
            database_date = query_date(info)
            # formats of database_date and info[date] is something like '2024/04/12'
            # turn the string to date type
            current_date = database_date.split('/')
            info_date = info['date'].split('/')
            # compare the date
            if current_date < info_date:
                print("The report need to be updated")
                detail_data = extract_data(data, info)

                res = update_report(info, detail_data)

            else:
                raise ce.TheReportIsNotNewestError("The report is not the newest")

        else:
            detail_data = extract_data(data, info)

            res = upload_report(info, detail_data)

    except ce.TheReportIsNotNewestError as e:
        print(f"The report is not the newest")
        traceback.print_exc()
        raise Exception(e.message)

    except ce.NotAllCoursesPassedError as e:
        print(f"Not all courses are passed")
        traceback.print_exc()
        raise Exception(e.message)

    except Exception as e:
        # delete the file
        os.remove(upload_path)
        traceback.print_exc()
        raise e
    else:
        # rename the file to info.sn.pdf and remove it to the score_report directory
        # if the file is existed in the score_report directory, it will be replaced
        score_report_path = os.path.join(score_report_directory, info['sn'] + '.pdf')
        if os.path.exists(score_report_path):
            os.remove(score_report_path)
    finally:
        os.rename(upload_path, score_report_path)

        # update the required field of the detail table according to the sn and the sn_rule

        return res


def get_grades_and_colleges():
    """Get all grades and colleges from the rule table"""
    conn = mysql_connection.connect_to_database()
    cursor = conn.cursor()
    # Call the get_grades_and_colleges function from rule.py
    res = rule.get_grades_and_colleges(cursor)
    cursor.close()
    return convert_to_cascader_options(res)


def convert_to_cascader_options(data):
    """Convert the grades and colleges into cascader options format"""
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


def get_rule_data(grade, college):
    """Get rule data based on the selected grade and college"""
    conn = mysql_connection.connect_to_database()
    try:
        cursor = conn.cursor()
        # Call the get_rule_data function from rule.py
        res = rule.get_rule_data(grade, college, cursor)
        return res
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        traceback.print_exc()
        raise e


def update_rule_data(data):
    """Update rule data changed by user in the rule table"""
    conn = mysql_connection.connect_to_database()
    try:
        cursor = conn.cursor()
        # Call the update_rule_data function from rule.py
        id = rule.update_rule_data(data, cursor)
        conn.commit()
        res = {'id': id}
        return res
    except Exception as e:
        conn.rollback()
        raise e


def update_required_score_and_sum(data):
    """Update the required field of the detail table and the score of the report table according to the data changed
    by user"""
    sns = get_sn_by_college_and_grade(data['college'], data['grade'])
    for sn in sns:
        set_required(sn, data)
        score = calculate_score(sn)
        update_score(sn, score)
        sum = calculate_sum(sn, data)
        update_sum(sn, sum)


def check_all_pass(detail_data):
    """every course must be passed"""
    for row in detail_data:
        if float(row[4]) < 60:
            return False
    return True


# select all sn from report table by the college and the grade
def get_sn_by_college_and_grade(college, grade):
    """get all sns from the report table by the college and the grade"""
    with mysql_connection.connect_to_database() as conn:
        with conn.cursor() as cursor:
            return report.get_sn_by_college_and_grade(college, grade, cursor)


def set_required(sn):
    """set the required field of the detail table according to the sn"""
    with mysql_connection.connect_to_database() as conn:
        with conn.cursor() as cursor:
            sn_report = report.get_sn_report_from_report_table(sn, cursor)

    with mysql_connection.connect_to_database() as conn:
        with conn.cursor() as cursor:
            sn_rule = rule.get_rule_data(sn_report['grade'], sn_report['college'], cursor)

    with mysql_connection.connect_to_database() as conn:
        with conn.cursor() as cursor:
            try:
                detail.modify_detail_message_required_field_by_course(sn, "形势与政策(1)", sn_rule['policy'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "形势与政策(2)", sn_rule['policy'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "形势与政策(3)", sn_rule['policy'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "形势与政策(4)", sn_rule['policy'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "形势与政策(5)", sn_rule['policy'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "形势与政策(6)", sn_rule['policy'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "形势与政策(7)", sn_rule['policy'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "形势与政策(8)", sn_rule['policy'], cursor)

                detail.modify_detail_message_required_field_by_course(sn, "体育(1)", sn_rule['pe'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "体育(2)", sn_rule['pe'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "体育(3)", sn_rule['pe'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "体育(4)", sn_rule['pe'], cursor)

                detail.modify_detail_message_required_field_by_course(sn, "军事技能", sn_rule['skill'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "军事理论", sn_rule['theory'], cursor)

                detail.modify_detail_message_required_field_by_type(sn, "选修", sn_rule['specialized'], cursor)
                detail.modify_detail_message_required_field_by_type(sn, "共修", sn_rule['public'], cursor)

            except Exception as e:
                conn.rollback()
                raise e
            else:
                res = "The required field is updated"
                conn.commit()
                return res


# set the required field of the detail table according to the sn and sn_rule
def set_required(sn, sn_rule):
    """set the required field of the detail table according to the sn and sn_rule"""
    print(sn_rule)
    with mysql_connection.connect_to_database() as conn:
        with conn.cursor() as cursor:
            try:
                detail.modify_detail_message_required_field_by_course(sn, "形势与政策(1)", sn_rule['policy'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "形势与政策(2)", sn_rule['policy'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "形势与政策(3)", sn_rule['policy'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "形势与政策(4)", sn_rule['policy'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "形势与政策(5)", sn_rule['policy'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "形势与政策(6)", sn_rule['policy'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "形势与政策(7)", sn_rule['policy'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "形势与政策(8)", sn_rule['policy'], cursor)

                detail.modify_detail_message_required_field_by_course(sn, "体育(1)", sn_rule['pe'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "体育(2)", sn_rule['pe'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "体育(3)", sn_rule['pe'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "体育(4)", sn_rule['pe'], cursor)

                detail.modify_detail_message_required_field_by_course(sn, "军事技能", sn_rule['skill'], cursor)
                detail.modify_detail_message_required_field_by_course(sn, "军事理论", sn_rule['theory'], cursor)

                detail.modify_detail_message_required_field_by_type(sn, "选修", sn_rule['specialized'], cursor)
                detail.modify_detail_message_required_field_by_type(sn, "公修", sn_rule['public'], cursor)

            except Exception as e:
                conn.rollback()
                raise e
            else:
                res = "The required field is updated"
                conn.commit()
                return res
            finally:
                cursor.close()


# get all detail messages from the detail table according to the sn
def get_sn_detail_from_detail_table(sn):
    """get all detail messages from the detail table according to the sn"""
    with mysql_connection.connect_to_database() as conn:
        with conn.cursor() as cursor:
            return detail.get_sn_detail_from_detail_table(sn, cursor)


# calculate the score of the student according to the sn
def calculate_score(sn):
    """calculate the score of the student according to the sn"""
    detail_data = get_sn_detail_from_detail_table(sn)
    total_point = 0
    total_grade = 0
    for row in detail_data:
        if row['required'] == 1:
            total_point += row['point']
            total_grade += row['grade'] * row['point']

    score = total_grade / total_point
    return score


# update the score of the student according to the sn
def update_score(sn, score):
    """update the score of the student according to the sn"""
    with mysql_connection.connect_to_database() as conn:
        with conn.cursor() as cursor:
            try:
                report.update_score({"sn": sn, "score": score}, cursor)
            except Exception as e:
                conn.rollback()
                raise Exception("An error occurred while updating the score")
            else:
                res = "The score is updated"
                conn.commit()
                return res
            finally:
                cursor.close()


def update_required_score_and_sum_of_sn(info):
    with mysql_connection.connect_to_database() as conn:
        with conn.cursor() as cursor:
            # update the required field of the detail table according to the sn and the sn_rule
            sn_rule = rule.get_rule_data(info['grade'], info['college'], cursor)
    set_required(info['sn'], sn_rule)
    # calculate the score of the student according to the sn
    score = calculate_score(info['sn'])
    # update the score of the student according to the sn
    update_score(info['sn'], score)
    # calculate the sum of the report table
    sum = calculate_sum(info['sn'], sn_rule)
    # update the comprehensive of the report table according to the info
    update_sum(info['sn'], sum)


# calculate the sum of the report table
def calculate_sum(sn, sn_rule):
    """calculate the sum of the report table"""
    with mysql_connection.connect_to_database() as conn:
        with conn.cursor() as cursor:
            sn_report = report.get_sn_report_from_report_table(sn, cursor)
    sum = sn_report['score'] * Decimal(sn_rule['score']) + sn_report['comprehensive'] * Decimal(
        sn_rule['comprehensive'])
    return sum


def update_sum(sn, sum):
    """update the sum of the report table according to the info"""
    with mysql_connection.connect_to_database() as conn:
        with conn.cursor() as cursor:
            try:
                report.update_sum({'sn': sn, 'sum': sum}, cursor)
            except Exception as e:
                conn.rollback()
                raise Exception("An error occurred while updating the sum")
            else:
                res = "The sum is updated"
                conn.commit()
                return res
            finally:
                cursor.close()


# select grade, college and major from the report table
# every itme is unique
def get_grade_college_major_from_report_table():
    with mysql_connection.connect_to_database() as conn:
        with conn.cursor() as cursor:
            return report.get_all_grade_college_major(cursor)


def convert_to_cascader_options_three_layer(data):
    # Sort the data by year (first element of each tuple)
    data_sorted = sorted(data, key=lambda x: (x[0], x[1], x[2]))  # Sort by year, college, and major

    options = []

    # Create a dictionary to store parent nodes based on the year
    parent_dict = {}

    for item in data_sorted:
        year, college, major = item
        label = f"{college} - {major}"
        value = label  # Use the label as the value

        # Check if the year exists as a parent node
        if year not in parent_dict:
            parent_dict[year] = {'label': str(year), 'value': str(year), 'children': []}

        # Check if the college exists as a child node under the year
        college_node = next((node for node in parent_dict[year]['children'] if node['label'] == college), None)

        if not college_node:
            college_node = {'label': college, 'value': college, 'children': []}
            parent_dict[year]['children'].append(college_node)

        # Add the major as a child node under the college
        major_node = {'label': major, 'value': major}  # Use the major as both label and value
        college_node['children'].append(major_node)

    # Convert parent_dict values to a list for the cascader options
    options = [{'label': v['label'], 'value': v['value'], 'children': v.get('children', [])} for v in
               parent_dict.values()]

    return options


# get the options of grade, college and major
def get_grade_college_major_options():
    """Get the options of grade, college and major"""
    data = get_grade_college_major_from_report_table()
    return convert_to_cascader_options_three_layer(data)


def get_report_data_by_grade_college_major(grade, college, major):
    """Get report data based on the selected grade, college and major"""
    conn = mysql_connection.connect_to_database()
    cursor = conn.cursor()
    try:
        # Call the get_report_data_by_grade_college_major function from report.py
        res = report.get_report_data_by_grade_college_major(grade, college, major, cursor)
        return res
    except Exception as e:
        error_message = f"An error occurred while getting report data by grade, college and major: {e}"
        print(error_message)
        raise Exception(error_message)
    finally:
        cursor.close()


# update comprehensive of the report table according to the sn
def update_comprehensive(data):
    """update the comprehensive of the report table according to the sn"""
    with mysql_connection.connect_to_database() as conn:
        with conn.cursor() as cursor:
            try:
                report.update_comprehensive(data, cursor)
                conn.commit()
                sn_rule = rule.get_rule_data(data['grade'], data['college'], cursor)
                sum = calculate_sum(data['sn'], sn_rule)
                update_sum(data['sn'], sum)
            except Exception as e:
                conn.rollback()
                raise Exception("An error occurred while updating the comprehensive")
            else:
                res = "The comprehensive is updated"
                conn.commit()
                return res
            finally:
                cursor.close()


def get_report_data_by_grade_college(grade, college):
    """Get report data based on the selected grade and college"""
    conn = mysql_connection.connect_to_database()
    cursor = conn.cursor()
    try:
        # Call the get_report_data_by_grade_college function from report.py
        res = report.get_report_data_by_grade_college(grade, college, cursor)
        return res
    except Exception as e:
        error_message = f"An error occurred while getting report data by grade and college: {e}"
        print(error_message)
        raise Exception(error_message)
    finally:
        cursor.close()


def get_majors_and_quantities(grade, college):
    """Get all majors and quantities from the allocation table based on the selected grade and college"""
    conn = mysql_connection.connect_to_database()
    cursor = conn.cursor()
    try:
        # Call the get_majors_and_quantities function from allocation.py
        res = allocation.get_majors_and_quantities(grade, college, cursor)
        return res
    except Exception as e:
        error_message = f"An error occurred while getting all majors and quantities: {e}"
        print(error_message)
        raise Exception(error_message)
    finally:
        cursor.close()


def get_allocation_data(grade, college):
    """Get allocation data based on the selected grade and college"""
    conn = mysql_connection.connect_to_database()
    cursor = conn.cursor()
    try:
        # Call the get_allocation_data function from allocation.py
        res = allocation.get_allocation_data(grade, college, cursor)
        return res
    except Exception as e:
        error_message = f"An error occurred while getting allocation data: {e}"
        print(error_message)
        raise Exception(error_message)
    finally:
        cursor.close()


def update_allocation_data(data):
    """Update allocation data in the allocation table"""
    conn = mysql_connection.connect_to_database()
    cursor = conn.cursor()
    try:
        # Call the update_allocation_data function from allocation.py
        allocation.update_allocation_data(data, cursor)
        conn.commit()
        res = "Allocation data updated successfully!"
        return res
    except Exception as e:
        conn.rollback()
        error_message = f"An error occurred while updating allocation data: {e}"
        print(error_message)
        raise Exception(error_message)
    finally:
        cursor.close()