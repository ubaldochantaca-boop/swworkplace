# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./analizador_contable.db"

# connect_args es indispensable para permitir que Streamlit lea mientras el script asíncrono escribe
Engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)
Base = declarative_base()

class Transaccion(Base):
    __tablename__ = "transacciones"
    
    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(String, index=True)
    descripcion = Column(String)
    monto = Column(Float)
    tipo = Column(String, index=True)       # gasto / deposito
    categoria = Column(String, index=True)  # Comida, Gasolinas, etc.
    nombre_archivo_pdf = Column(String)

# Índice compuesto de alta velocidad
Index('idx_analisis_contable', Transaccion.fecha, Transaccion.tipo, Transaccion.categoria)

def init_db():
    Base.metadata.create_all(bind=Engine)

if __name__ == "__main__":
    init_db()
    print("[+] Base de datos e índices inicializados correctamente desde el módulo independiente.")