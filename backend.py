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

if __name__ == '__main__':
    app.run(debug=True)
