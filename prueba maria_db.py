from database.schema import create_tables
from models.user_model import UserModel


create_tables()

print("Tablas verificadas correctamente.")

resultado = UserModel.create_user(
    nombre="Mauricio Prueba",
    usuario="mauri",
    correo="mauri@test.local",
    password="123456"
)

print(resultado)

login = UserModel.login("mauri", "123456")

print(login)