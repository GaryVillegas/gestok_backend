from database.db_mysql import get_connection
from models.Account import Account

class AccountService:
    """
    Servicio de cuentas que maneja la lógica de negocio
    para creación, actualización, lectura y eliminación de cuentas de usuario (Datos de usuario)
    """
    
    @classmethod
    def create_account(cls, account, user_id: int):
        try:
            #Obtenemos conexion a bbddd
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("call sp_create_account(%s, %s, %s, %s)", (account['name'], account['lastname'], account['rut'], user_id,))
                row = cursor.fetchone()
                if row is None:
                    return None, "Error al crear cuenta."
                account_id = row[0]
                connection.commit()
                return {
                    'account_id': account_id,
                }, "Cuenta creada con exito"
        except Exception as ex:
            print(f"Exception. Type {str(type)}: {str(ex)}")
            if connection:
                connection.rollback()
            return None, "Error en el servidor"
        finally:
            if connection:
                connection.close()

    @classmethod
    def get_account(cls, user_id: int):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("call sp_get_account(%s)", (user_id,))
                row = cursor.fetchone()
                #Se valida que row venga sin datos
                if row is None:
                    #Al no tener datos, lanzar None
                    return None, "No se encontro la cuenta."
                #Al tener datos, armarlos
                id, name, lastname, rut = row
                # Confirmar la transacción en la base de datos
                connection.commit()
                #Armar los datos segun modelo y retornarlos
                account = Account(id, name, lastname, rut, user_id)
                return {
                    'account': account.to_dict(),
                }, "Se encontro la cuenta!"
        except Exception as ex:
            # Manejo de errores durante la autenticación
            print(f"Exception. Type {type(ex)}: {str(ex)}")
            if connection:
                connection.rollback()  # Revertir cualquier cambio pendiente
            return None, "Error en el servidor"
        finally:
            # Asegurar que la conexión se cierre siempre
            if connection:
                connection.close()

    @classmethod
    def delete_account(cls, user_id: int):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("call sp_delete_account(%s)", (user_id,))
                affected_row = cursor.rowcount
                connection.commit()
                if affected_row:
                    return {
                        'row affected': affected_row,
                    }, "Se elimino cuenta."
                return None, "Error al eliminar cuenta."
        except Exception as ex:
            print(f"Exception. Type {str(type)}: {str(ex)}")
            if connection:
                connection.rollback()
            return None, "Error en el servidor"
        finally:
            if connection:
                connection.close()