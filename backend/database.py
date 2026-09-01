import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# ---------------------------------------------------------------------
# 1) LA URL DE CONEXIÓN
# ---------------------------------------------------------------------
# Formato general de cualquier URL de conexión a Postgres:
#   postgresql://<usuario>:<password>@<host>:<puerto>/<nombre_bd>
#
# os.getenv("DATABASE_URL", "...") busca esa variable de entorno.
# ¿De dónde sale? La definiste en docker-compose.yml, en el servicio
# "backend":
#
#   environment:
#     DATABASE_URL: postgresql://usuario_inventario:password_seguro@db:5432/inventario_db
#
# Docker Compose INYECTA esa variable dentro del contenedor del backend
# como si hubieras hecho "export DATABASE_URL=..." en una terminal Linux.
# Python la lee con os.getenv. El segundo argumento es solo un valor de
# RESPALDO por si algún día corres esto fuera de Docker.
#
# Nota el host: "db", no "localhost". "db" es el NOMBRE DEL SERVICIO en
# docker-compose.yml, y Docker resuelve ese nombre a la IP interna del
# contenedor de Postgres automáticamente.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://usuario_inventario:password_seguro@db:5432/inventario_db",
)


# ---------------------------------------------------------------------
# 2) EL ENGINE
# ---------------------------------------------------------------------
# El "engine" es el objeto que SQLAlchemy usa para conectarse a la BD. 
# y create_engine() prepara el mecanismo para que Python pueda comunicarse con él.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


# ---------------------------------------------------------------------
# 3) SessionLocal: la fábrica de sesiones
# ---------------------------------------------------------------------
# Una "Session" es como una conversación temporal con la BD: la abres,
# haces queries/inserts, y la cierras. NO se comparte entre requests
# distintos (dos usuarios usando la misma sesión mezclaría datos).
#
# sessionmaker(...) no crea una sesión todavía: crea una CLASE
# (SessionLocal) que, cada vez que la llamas como SessionLocal(), te
# entrega una sesión nueva. Es un patrón de fábrica.
#
# autocommit=False: cada cambio queda "pendiente" hasta que llames
# db.commit() explícitamente. Esto permite, por ejemplo, hacer un
# descuento de stock Y un registro de venta como una sola operación
# atómica: si algo falla, haces db.rollback() y ninguno de los dos
# cambios queda guardado.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ---------------------------------------------------------------------
# 4) Base: la clase de la que heredan TODOS los modelos
# ---------------------------------------------------------------------
# Cuando en models.py escribes "class Sucursales(Base):", SQLAlchemy
# registra esa clase dentro de Base.metadata -- un catálogo interno de
# todas las tablas que la app conoce.
#
# ES CRÍTICO que exista UNA SOLA Base en todo el proyecto. Si models.py
# creara su propia Base independiente, SQLAlchemy tendría dos catálogos
# separados que no se reconocen entre sí, y las relationship() fallarían.
Base = declarative_base()


# ---------------------------------------------------------------------
# 5) get_db(): la función que usará FastAPI en cada endpoint
# ---------------------------------------------------------------------
# Se usa así en un endpoint:
#
#   @app.get("/sucursales")
#   def listar(db: Session = Depends(get_db)):
#       return db.query(Sucursales).all()
#
# ¿Por qué "yield" y no "return"? Porque FastAPI necesita ejecutar código
# ANTES de que el endpoint use la sesión (crearla) y DESPUÉS de que
# termine (cerrarla), sin importar si el endpoint tuvo éxito o lanzó un
# error. "yield" pausa la función, entrega "db" al endpoint, y cuando el
# endpoint termina, retoma la ejecución en la siguiente línea (finally).
#
# El try/finally garantiza que db.close() se ejecute SIEMPRE, evitando
# conexiones "abandonadas" abiertas hacia Postgres.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()