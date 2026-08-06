import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.preference_model import PreferenceModel
from models.user_model import UserModel
import json

superuser = UserModel.get_user_by_username_or_email("superuser@softrelief.local")
if not superuser:
    print("No se encontró la cuenta superuser@softrelief.local")
    sys.exit(1)

id_usuario = superuser["id_usuario"]
nombre_original = superuser["nombre"]
usuario_original = superuser.get("nombre_usuario", superuser["correo"])
correo_original = superuser["correo"]
tema_original = superuser.get("tema_visual", "light")

print("=== Estado original ===")
print("id_usuario:", id_usuario)
print("nombre:", nombre_original)
print("correo:", correo_original)
print("tema:", tema_original)

print("\n=== Pruebas (NO destructivas: restauran los valores originales) ===")
print('get_account_settings:', json.dumps(UserModel.get_account_settings(id_usuario), ensure_ascii=False, default=str))
print('update_account_settings:', json.dumps(UserModel.update_account_settings(id_usuario, "Cuenta Temporal Prueba", "temporalprueba", "temporal@prueba.com"), ensure_ascii=False, default=str))
print('update_theme:', json.dumps(PreferenceModel.update_theme(id_usuario, "dark" if tema_original == "light" else "light"), ensure_ascii=False, default=str))

print("\n=== Restaurando valores originales ===")
print(UserModel.update_account_settings(id_usuario, nombre_original, usuario_original, correo_original))
print(PreferenceModel.update_theme(id_usuario, tema_original))

final = UserModel.get_user_by_username_or_email("superuser@softrelief.local")
print("\n=== Estado final (debe coincidir con el original) ===")
print("nombre:", final["nombre"])
print("correo:", final["correo"])
print("tema:", final["tema_visual"])
