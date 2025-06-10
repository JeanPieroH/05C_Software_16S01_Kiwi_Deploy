from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.future import select
from sqlalchemy import text # Importar text para ejecutar SQL plano


from config.settings import get_settings

settings = get_settings()

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)

# Sesiones asincronas para la base de datos
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Crear la clase base para los modelos
Base = declarative_base()

async def init_db():
    """
    Inicializa la base de datos creando todas las tablas definidas
    """
    print("Intentando crear todas las tablas de la base de datos...")

    async with engine.begin() as conn:
        try:
            await conn.execute(text("SET search_path TO public;"))
            #await conn.run_sync(Base.metadata.create_all)
            print("Todas las tablas han sido creadas.")
        except Exception as e: # ¡Cambia 'except:' por 'except Exception as e:'!
            print(f"No se pudo crear las tablas. Error: {e}") # Imprime el error real

async def get_db():
    """
    Generador de dependencia para obtener una sesión de base de datos
    """
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()

async def drop_db():

    print("Intentando eliminar todas las tablas de la base de datos...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("Todas las tablas han sido eliminadas.")