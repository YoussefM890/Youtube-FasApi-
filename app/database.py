from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URI = "postgresql://<username>:<password>@<ip-address/hosname>/<database_name>"
SQLALCHEMY_DATABASE_URI = "postgresql://postgres:youssef@localhost/YoutubeChannels"
engine = create_engine(SQLALCHEMY_DATABASE_URI)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()
