from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from view.function import function


app = Flask(__name__)
swagger = Swagger(app)
CORS(app)

# Register the blueprint
app.register_blueprint(function)

if __name__ == '__main__':
    app.run(debug=True)
