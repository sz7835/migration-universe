from flask_sqlalchemy import SQLAlchemy

# Declare the db object
db = SQLAlchemy()

# Set your remote MySQL DB URI here
DB_URI = 'mysql+pymysql://root:Delt%402023@161.132.202.110:3306/deltanet'

# Initialize Flask app with DB config
def init_app(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
