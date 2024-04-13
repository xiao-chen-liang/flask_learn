from werkzeug.datastructures import FileStorage
import pdfplumber
from openpyxl import Workbook
import os

upload_directory = 'uploads'
score_report_directory = 'score_report'


def handle_file(file: FileStorage):
    try:
        filename = file.filename
        upload_path = os.path.join(upload_directory, filename)
        score_report_path = os.path.join(score_report_directory, filename)

        file.save(upload_path)

        with pdfplumber.open(upload_path) as pdf:
            first_page = pdf.pages[0]
            data = first_page.extract_table()

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

        # Write data to the worksheet
        for row_index, row_data in enumerate(last_data):
            for col_index, value in enumerate(row_data):
                ws.cell(row=row_index + 1, column=col_index + 1, value=value)

        # Save the workbook to a file
        wb.save("fact.xlsx")

    except Exception as e:
        raise e
    else:
        return 1


