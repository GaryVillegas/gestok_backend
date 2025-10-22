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

    @classmethod
    def delete_store(cls, store_id: int):
        try:
            #Connection to database
            connection = get_connection()
            #Establish connection cursor as cursor
            with connection.cursor() as cursor:
                #Calling database sp to delete store with store id
                cursor.execute("call sp_delete_store(%s)", (store_id,))
                #Fetch the result
                result = cursor.fetchone()
                connection.commit()
                #if there are result and are mayor to 0 return the row affected
                if result:
                    row_affected = result[0]
                    if row_affected > 0:
                        return row_affected, "Se elimino tienda exitosamente."
                    #if are less or equal to 0, return message
                    else:
                        return 0, "No se encontraron datos para eliminar"
                
                #If are no result, that mean we have an error in database or code.
                return 0, "Error al eliminar tienda."
        except Exception as ex:
            #Retrun exceptions
            print(f"Exception. type{str(type)}: {str(ex)}")
            if connection:
                connection.rollback()
            return None, "Error en el servidor"
        finally:
            #Close connection to database
            if connection:
                connection.close()