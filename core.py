from werkzeug.datastructures import FileStorage
import pdfplumber
from openpyxl import Workbook
import os
import mysql_connection
import persistence.report as report
import persistence.rule as rule
import persistence.detail as detail
import re

upload_directory = 'uploads'
score_report_directory = 'score_report'

connection = mysql_connection.connect_to_database()


def handle_file(file: FileStorage):
    try:
        filename = file.filename
        upload_path = os.path.join(upload_directory, filename)
        score_report_path = os.path.join(score_report_directory, filename)

        file.save(upload_path)

        with pdfplumber.open("D:\\file\\flask_learn\\uploads\\score_20180152016_2024-04-12_10_44_17.pdf") as pdf:
            text = pdf.pages[0].extract_text()
            data = pdf.pages[0].extract_table()

        # Split the multi-line string into lines and select the first 4 lines
        first_4_lines = text.splitlines()[:4]

        info = {}  # Dictionary to store extracted information

        for line in first_4_lines:
            if '学院' in line:
                info['collage'] = line.split('学院: ')[1].split(' ')[0]
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
                info['data'] = line.split('打印日期:')[1].split(' ')[0]

        # Use regular expression to find four continuous digits
        match = re.search(r'\d{4}', info['grade'])
        info['grade'] = int(match.group()) if match else None

        print(info)

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

        print(detail_data)

        # Call the add_report_message_to_report_table function from report.py
        report.add_report_message_to_report_table(connection, info)
        # Call the add_detail_message_to_detail_table function from detail.py
        detail.add_detail_message_to_detail_table(connection, detail_data)
        # Call the add_collage_and_grade_to_rule_table function from rule.py
        rule.add_collage_and_grade_to_rule_table(connection, info)

        connection.close()

    except Exception as e:
        raise e
    else:
        return 1


