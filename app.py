import os
from app import create_app

# Tomar la configuración de la variable de entorno FLASK_CONFIG o usar 'production' por defecto
config_name = os.getenv("FLASK_CONFIG", "production")

# Crear la app usando la factory
app = create_app(config_name=config_name)

if __name__ == "__main__":
    # Solo para desarrollo local
    app.run(debug=(config_name == "development"))