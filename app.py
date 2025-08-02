from flask import Flask
from config import init_app
from routes import catalogo_bp

app = Flask(__name__)
init_app(app)  # Connects to the MySQL Deltanet DB

# Register all blueprints here
app.register_blueprint(catalogo_bp)

if __name__ == "__main__":
    app.run(port=5055, debug=True)
