
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME')}"
    )
    DEBUG = True


class ProductionConfig(Config):
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback_prod_secret")
    
    # OPCIÓN A: Para Render/Heroku y similares que proveen DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Convertir de postgres:// a postgresql:// que es lo que SQLAlchemy necesita
        SQLALCHEMY_DATABASE_URI = database_url.replace("postgres://", "postgresql://")
    else:
        # OPCIÓN B: Para otros servicios o desarrollo (manteniendo compatibilidad)
        SQLALCHEMY_DATABASE_URI = (
            f"postgresql+psycopg2://{os.getenv('PROD_DB_USER')}:{os.getenv('PROD_DB_PASSWORD')}"
            f"@{os.getenv('PROD_DB_HOST')}:{os.getenv('PROD_DB_PORT', '5432')}/{os.getenv('PROD_DB_NAME')}"
        )
    
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///test.db")


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
