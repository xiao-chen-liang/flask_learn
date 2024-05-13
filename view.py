import traceback
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import controller
import handle_report


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
            res = handle_report.handle_file(file)
        return res, 200
    except Exception as e:
        error_message = f"{str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({'error': error_message}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.route('/get_grades_and_colleges')
def get_rules():
    try:
        return jsonify(controller.get_grades_and_colleges())
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({'error': error_message}), 500

@app.route('/get_rule_data/<string:grade>/<string:college>')
def get_rule_data(grade, college):
    try:
        rule_response = controller.get_rule_data(grade, college)
        if rule_response:
            return jsonify(rule_response)
        else:
            return jsonify({'error': 'Rule data not found for the selected grade and college'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_rule_data', methods=['POST'])
def update_rule_data():
    try:
        data = request.get_json()
        controller.update_rule_data(data)
        controller.update_required_score_and_sum(data)
        return "Rule data and detail data updated successfully!", 200
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({'error': error_message}), 500

@app.route('/get_options_of_grades_colleges_majors')
def get_options_of_grades_colleges_majors():
    try:
        return jsonify(controller.get_grade_college_major_options())
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({'error': error_message}), 500

@app.route('/get_rule_data_by_grade_college_major/<string:grade>/<string:college>/<string:major>')
def get_report_data_by_grade_college_major(grade, college, major):
    try:
        rule_response = controller.get_report_data_by_grade_college_major(grade, college, major)
        if rule_response:
            return jsonify(rule_response)
        else:
            return jsonify({'error': 'Rule data not found for the selected grade, college and major'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_report_data_by_grade_college/<string:grade>/<string:college>')
def get_report_data_by_grade_college(grade, college):
    try:
        rule_response = controller.get_report_data_by_grade_college(grade, college)
        if rule_response:
            return jsonify(rule_response)
        else:
            return jsonify({'error': 'Rule data not found for the selected grade and college'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update_comprehensive', methods=['PUT'])
def update_comprehensive():
    try:
        data = request.get_json()
        controller.update_comprehensive(data)
        return "Comprehensive scontroller updated successfully!", 200
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({'error': error_message}), 500

@app.route('/get_allocation_data/<string:grade>/<string:college>')
def get_allocation_data(grade, college):
    try:
        return jsonify(controller.get_allocation_data(grade, college))
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({'error': error_message}), 500

@app.route('/update_allocation_data', methods=['PUT'])
def update_allocation_data():
    try:
        data = request.get_json()
        controller.update_allocation_data(data)
        return "Allocation data updated successfully!", 200
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({'error': error_message}), 500

@app.route('/download', methods=['POST'])
def download_file():
    try:
        outputData = request.get_json()
        download_path = controller.generate_output_file(outputData)
        return send_file(download_path, as_attachment=True)
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({'error': error_message}), 500

@app.route('/get_detail_messages/<string:sn>')
def get_detail_messages(sn):
    try:
        return jsonify(controller.get_sn_detail_from_detail_table(sn))
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({'error': error_message}), 500

@app.route('/update_required', methods=['POST'])
def update_required():
    try:
        data = request.get_json()
        controller.update_required_by_sn(data)
        return "Required updated successfully!", 200
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        traceback.print_exc()
        return jsonify({'error': error_message}), 500


if __name__ == '__main__':
    app.run(debug=True)
