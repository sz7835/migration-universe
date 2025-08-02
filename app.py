from flask import Flask
from routes import catalogo_routes
from flask_cors import CORS
from config import db, DB_URI

app = Flask(__name__)
CORS(app)

# Configure DB and initialize
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Register your routes
app.register_blueprint(catalogo_routes)

if __name__ == "__main__":
    app.run(debug=True, port=5055)
