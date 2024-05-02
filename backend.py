from flask import Flask, request, jsonify
from flask_cors import CORS
import core
import traceback

app = Flask(__name__)
CORS(app)


@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return 'No file part', 400

        files = request.files.getlist('file')
        if len(files) == 0:
            return 'No files uploaded', 400

        for file in files:
            if file.filename == '':
                return 'No selected file', 400

            # Call the handle_file function from core.py
            res = core.handle_file(file)

        return res, 200

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({'error': error_message}), 500


# Custom error handler for 404 Not Found error
@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404


# Custom error handler for 500 Internal Server Error
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


@app.route('/get_grades_and_colleges')
def get_rules():
    try:
        return jsonify(core.get_grades_and_colleges())
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"

        print(error_message)
        traceback.print_exc()
        return jsonify({'error': error_message}), 500


# Mock data for demonstration
rule_data = {
    ('2020', '大数据与智能工程学院'): {'policy': 1, 'pe': 0, 'skill': 1},
    ('2021', '大数据与智能工程学院'): {'policy': 0, 'pe': 1, 'skill': 0},
    # Add more data as needed
}


@app.route('/get_rule_data/<string:grade>/<string:college>')
def get_rule_data(grade, college):
    try:
        # Get rule data based on the selected grade and college
        # rule_response = rule_data.get((grade, college))
        rule_response = core.get_rule_data(grade, college)
        if rule_response:
            return jsonify(rule_response)
        else:
            return jsonify({'error': 'Rule data not found for the selected grade and college'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/update_rule_data', methods=['POST'])
def update_rule_data():
    try:
        # Get the JSON data from the request body
        data = request.get_json()

        # Assuming `data` contains the updated rule data
        # You can then pass this data to your core function to update the rule table
        # Example:
        # core.update_rule_data(data)

        # pass the data to core.py to update the rule data
        core.update_rule_data(data)
        core.update_required_score_and_sum(data)
        return "Rule data and detail data updated successfully!", 200

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({'error': error_message}), 500


# get options of grades, colleges and majors
@app.route('/get_options_of_grades_colleges_majors')
def get_options_of_grades_colleges_majors():
    try:
        return jsonify(core.get_grade_college_major_options())
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({'error': error_message}), 500


# define a method to receive grade, college and major
# the arguments are passed in the URL
@app.route('/get_rule_data_by_grade_college_major/<string:grade>/<string:college>/<string:major>')
def get_report_data_by_grade_college_major(grade, college, major):
    try:
        # Get rule data based on the selected grade, college and major
        rule_response = core.get_report_data_by_grade_college_major(grade, college, major)
        if rule_response:
            return jsonify(rule_response)
        else:
            return jsonify({'error': 'Rule data not found for the selected grade, college and major'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# define a method to receive grade, college and return the reports
# the arguments are passed in the URL
@app.route('/get_report_data_by_grade_college/<string:grade>/<string:college>')
def get_report_data_by_grade_college(grade, college):
    try:
        # Get rule data based on the selected grade and college
        rule_response = core.get_report_data_by_grade_college(grade, college)
        if rule_response:
            return jsonify(rule_response)
        else:
            return jsonify({'error': 'Rule data not found for the selected grade and college'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# const response = await axios.put(updateUrl, { comprehensive: row.inputValue, sn: row.sn});
# const updateUrl = `http://localhost:5000/update_comprehensive/`;
@app.route('/update_comprehensive', methods=['PUT'])
def update_comprehensive():
    try:
        # Get the JSON data from the request body
        data = request.get_json()

        # Assuming `data` contains the updated comprehensive score and student number
        # You can then pass this data to your core function to update the comprehensive score
        # Example:
        # core.update_comprehensive(data)

        # pass the data to core.py to update the comprehensive score
        core.update_comprehensive(data)
        return "Comprehensive score updated successfully!", 200

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({'error': error_message}), 500


# get allocation data by grade and college
@app.route('/get_allocation_data/<string:grade>/<string:college>')
def get_allocation_data(grade, college):
    try:
        return jsonify(core.get_allocation_data(grade, college))
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({'error': error_message}), 500

# update allocation data
@app.route('/update_allocation_data', methods=['PUT'])
def update_allocation_data():
    try:
        # Get the JSON data from the request body
        data = request.get_json()

        # Assuming `data` contains the updated allocation data
        # You can then pass this data to your core function to update the allocation table
        # Example:
        # core.update_allocation_data(data)

        # pass the data to core.py to update the allocation data
        core.update_allocation_data(data)
        return "Allocation data updated successfully!", 200

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({'error': error_message}), 500


if __name__ == '__main__':
    app.run(debug=True)
