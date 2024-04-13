from flask import Flask
from flask import request
from flask_cors import CORS
import core

app = Flask(__name__)
CORS(app)
app.app_context().push()

print(__name__ + " ATTENTION")

@app.route('/')
def hello():
    print('Hello, World!')
    return 'Hello, World!'


@app.route('/upload', methods=['POST'])
def upload_file():
    print("upload_file called")
    if 'file' not in request.files:
        return 'No file part'

    # Get the list of files
    files = request.files.getlist('file')

    # Check if any files were uploaded
    if len(files) == 0:
        return 'No files uploaded'



    try:
        # Iterate over the files and print their names
        for file in files:
            if file.filename == '':
                return 'No selected file'
            print("File name:", file.filename)

            # Call the handle_file function from core.py
            core.handle_file(file)
        return 'Files uploaded successfully'

    except Exception as e:
        return str(e)



if __name__ == '__main__':
    print("Starting Flask server in debug mode...")
    app.run(debug=True)

