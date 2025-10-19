from database.db_mysql import get_connection
from models.Account import Account

class AccountService:
    """
    Servicio de cuentas que maneja la lógica de negocio
    para creación, actualización, lectura y eliminación de cuentas de usuario (Datos de usuario)
    """
    