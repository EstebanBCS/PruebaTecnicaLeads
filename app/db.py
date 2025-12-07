import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


#cargar variables desde archivo .env
load_dotenv
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:TU_PASSWORD@localhost:5432/leads_db"
)


engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
