# -*- mode: python ; coding: utf-8 -*-
#
# SoftRelief.spec — build PyInstaller ONE-FILE (un solo SoftRelief.exe)
#
# Hallazgos del analisis de dependencias:
#   - Las vistas se cargan DINAMICAMENTE en views/home_view.py via import_module()
#     ("views.specialist_view", "views.checkin_view", etc.) -> PyInstaller no las
#     ve por analisis estatico: hay que declararlas como hiddenimports.
#   - Los juegos (games/*.py) se cargan como fuente desde el filesystem en
#     views/microbreaks_view.py (spec_from_file_location) -> se envian como DATA.
#   - mysql.connector carga sus plugins de autenticacion y locales dinamicamente
#     (caching_sha2_password, mysql_native_password, locales.eng.client_error,
#     kerberos, etc.) -> collect_all("mysql.connector").
#   - cryptography lo requiere el plugin caching_sha2_password en runtime.
#   - customtkinter trae temas/assets propios -> collect_all("customtkinter").
#   - assets/ (fondos, logo, iconos y musica) -> DATA.
#   - .env se embebe en el bundle; en runtime connection.py da prioridad a un
#     .env externo colocado junto al SoftRelief.exe.

import os

from PyInstaller.utils.hooks import collect_all, collect_submodules

ROOT = os.path.abspath(SPECPATH) if "SPECPATH" in globals() else os.getcwd()

datas = []
binaries = []
hiddenimports = []

# ---------------------------------------------------------------
# mysql.connector: plugins de auth + locales (carga dinamica)
# ---------------------------------------------------------------
mysql_datas, mysql_binaries, mysql_hidden = collect_all("mysql.connector")
datas += mysql_datas
binaries += mysql_binaries
hiddenimports += mysql_hidden

# ---------------------------------------------------------------
# customtkinter: temas y assets propios del widget toolkit
# ---------------------------------------------------------------
ctk_datas, ctk_binaries, ctk_hidden = collect_all("customtkinter")
datas += ctk_datas
binaries += ctk_binaries
hiddenimports += ctk_hidden

# ---------------------------------------------------------------
# cryptography: usado por caching_sha2_password en runtime
# ---------------------------------------------------------------
hiddenimports += ["cryptography"]

# ---------------------------------------------------------------
# Vistas: main.py solo importa login/home; el resto se carga con
# import_module() en home_view.open_view() -> hiddenimports
# ---------------------------------------------------------------
hiddenimports += [
    "views.login_view",
    "views.register_view",
    "views.home_view",
    "views.specialist_view",
    "views.checkin_view",
    "views.microbreaks_view",
    "views.history_view",
    "views.settings_view",
    "views.calm_mode_view",
    "views.breathing_view",
    "views.sounds_view",
    "views.superuser_view",
]

# ---------------------------------------------------------------
# Controladores, modelos y capa de datos (mongo incluido)
# ---------------------------------------------------------------
hiddenimports += collect_submodules("controllers")
hiddenimports += collect_submodules("models")
hiddenimports += ["database.connection", "database.mongo_connection", "database.schema"]

# ---------------------------------------------------------------
# assets: imagenes, iconos y musica
# ---------------------------------------------------------------
datas.append((os.path.join(ROOT, "assets"), "assets"))

# ---------------------------------------------------------------
# games: se cargan como fuente desde el filesystem (microbreaks_view)
# ---------------------------------------------------------------
games_dir = os.path.join(ROOT, "games")
for name in sorted(os.listdir(games_dir)):
    if name.endswith(".py"):
        datas.append((os.path.join(games_dir, name), "games"))

# ---------------------------------------------------------------
# .env embebido (un .env junto al exe tiene prioridad en runtime)
# ---------------------------------------------------------------
env_file = os.path.join(ROOT, ".env")
if os.path.exists(env_file):
    datas.append((env_file, "."))

# ---------------------------------------------------------------
# Analysis + EXE one-file
# ---------------------------------------------------------------
a = Analysis(
    ["main.py"],
    pathex=[ROOT],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=["tests", "docs", "pytest"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="SoftRelief",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
