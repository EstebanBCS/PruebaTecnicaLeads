import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


#cargar variables desde archivo .env
load_dotenv()

#obtener URL de la BD desde la variable de entorno
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:TU_PASSWORD@localhost:5432/leads_db"
)

#crear motor de conexion
engine = create_engine(DATABASE_URL, echo=False)

#crear sesion local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#base para declarar modelos
Base = declarative_base()
