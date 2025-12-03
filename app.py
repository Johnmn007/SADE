import os
from app import create_app

# Render usa FLASK_ENV o FLASK_CONFIG (tú usas FLASK_CONFIG)
config_name = os.getenv("FLASK_CONFIG", "production")

app = create_app(config_name)
from app import create_app
import os

# Tomar la configuración de la variable de entorno FLASK_CONFIG o usar 'production' por defecto
config_name = os.getenv("FLASK_CONFIG", "production")

# Crear la app usando la factory
app = create_app(config_name=config_name)
