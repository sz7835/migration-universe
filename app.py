from flask import Flask
from routes import catalogo_routes
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Register routes
app.register_blueprint(catalogo_routes)

if __name__ == '__main__':
    app.run(debug=True, port=5055)

