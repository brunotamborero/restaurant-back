from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
SQLALCHEMY_DATABASE_URL = "postgresql://bruno:postgres@localhost:5432/postgres"
#SQLALCHEMY_DATABASE_URL = "postgresql://mljrkxltpcsenm:1eb54b29f23edcc535d7b4d6a9d92494c5708b8332eea21b5efd654a90d2b587@ec2-54-74-14-109.eu-west-1.compute.amazonaws.com:5432/dbce4kjl6q6ejq"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
