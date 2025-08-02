# config.py

from sqlalchemy import create_engine

# Connection string without password
DATABASE_URL = "mysql+pymysql://root:@161.132.202.110:3306/deltanet"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
