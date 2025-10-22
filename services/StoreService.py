from database.db_mysql import get_connection
from models.Store import Store

class StoreService:
    """
    Servicio de tienda que maneja
    la logica de negocio de creacion, lectura y eliminacion de tienda
    """
    @classmethod
    def create_store(cls, store, user_id: int):
        try:
            #Obtenemos conexion a base de datos
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("call sp_create_store(%s, %s, %s)", (store['description'], store['address'], user_id))
                row = cursor.fetchone()
                if row is None:
                    return None, "Error al crear tienda."
                id = row[0]
                connection.commit()
                return id, "Tienda creada con exito."
        except Exception as ex:
            print(f"Exception. Type {str(type)}: {str(ex)}")
            if connection:
                connection.rollback()
            return None, "Error en el servidor"
        finally:
            if connection:
                connection.close()
    
    @classmethod
    def get_store(cls, user_id: int):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("call sp_get_store(%s)", (user_id))
                row = cursor.fetchone()
                if row is None:
                    return None, "Error al traer tienda."
                id, description, address = row
                store = Store(id, description, address, user_id)
                return store, "Tienda encontrada!"
        except Exception as ex:
            print(f"Exception. type{str(type)}: {str(ex)}")
            return None, "Erro en el servidor"
        finally:
            if connection:
                connection.close()

#TODO: crear la funcion para eliminar tienda.