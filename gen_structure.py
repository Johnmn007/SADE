#!/usr/bin/env python3
import os

# Carpetas y archivos a ignorar
IGNORAR = {
    "__pycache__",
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    "venv"
}

# Extensiones de archivo a ignorar
IGNORAR_EXT = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".log",
    ".ini"
}

def debe_ignorar(nombre):
    """
    Determina si un archivo o carpeta debe ser ignorado.
    """
    # Ignorar por nombre
    if nombre in IGNORAR:
        return True
    
    # Ignorar por extensión
    _, extension = os.path.splitext(nombre)
    if extension in IGNORAR_EXT:
        return True
    
    return False


def generar_arbol(ruta, prefijo=""):
    """
    Genera la estructura de árbol para la ruta dada.
    """
    elementos = sorted([
        e for e in os.listdir(ruta)
        if not debe_ignorar(e)
    ])

    elementos_count = len(elementos)

    for i, elemento in enumerate(elementos):
        ruta_completa = os.path.join(ruta, elemento)
        es_ultimo = (i == elementos_count - 1)

        conector = "└── " if es_ultimo else "├── "
        print(prefijo + conector + elemento)

        if os.path.isdir(ruta_completa):
            extension_prefijo = "    " if es_ultimo else "│   "
            generar_arbol(ruta_completa, prefijo + extension_prefijo)


def main():
    ruta_actual = os.getcwd()
    print(f"Estructura de {ruta_actual}:\n")
    generar_arbol(ruta_actual)


if __name__ == "__main__":
    main()
