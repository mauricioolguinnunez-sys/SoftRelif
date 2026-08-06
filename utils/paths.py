import os
import sys


def app_base_dir():
    """
    Directorio base de la aplicación:

    - Modo congelado (PyInstaller .exe): junto al ejecutable,
      para que los archivos de estado y configuración persistan.
    - Modo desarrollo: raíz del proyecto.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def app_exec_dir():
    """
    Directorio del ejecutable actual:
    - Modo congelado: directorio del .exe.
    - Modo desarrollo: directorio del intérprete de Python.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(sys.executable))
