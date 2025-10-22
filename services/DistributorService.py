from database.db_mysql import get_connection
from models.Distributor import Distributor

class DistributorService:
    """
    Servico de distribuidor para manejar la logica de negocio
    """
    @classmethod
    def create_distributor(cls, distributor, user_id: int):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("call sp_create_distributor(%s, %s)", (distributor['description'], user_id,))
                row = cursor.fetchone()
                if row is None:
                    return None, "Error al crear distribuidor."
                id = row[0]
                connection.commit()
                return id, "Distribuidor creado con exito."
        except Exception as ex:
            print(f"Exception. Type{str(type)}: {str(ex)}")
            if connection:
                connection.rollback()
            return None, "Error en el servidor."
        finally:
            if connection:
                connection.close()

    @classmethod
    def get_distributor(cls, user_id: int):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("call sp_get_distributor(%s)", (user_id,))
                rows = cursor.fetchall()
                if not rows:
                    return None, "No se encontraron distribuidores."
                
                distributors = [
                    Distributor(row[0], row[1], user_id)
                    for row in rows
                ]
                return distributors, "Se encontraron distribuidores."
        except Exception as ex:
            print(f"Exception. Type{str(type)}: {str(ex)}")
            if connection:
                connection.rollback()
            return None, "Error en el servidor"
        finally:
            if connection:
                connection.close()

    @classmethod
    def delete_distributor(cls, distributir_id: int):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("call sp_delete_distributor(%s)", (distributir_id,))
                row = cursor.fetchone()
                connection.commit()
                if row:
                    row_affected = row[0]
                    if row_affected > 0:
                        return row_affected, "Se elimino el distribuidor."
                    else:
                        return 0, "No se encontraron datos para eliminar."
                
                return 0, "Error al eliminar distribuidor"
        except Exception as ex:
            print(f"Exception. Type{str(type)}: {str(ex)}")
            if connection:
                connection.rollback()
            return None, "Error en el servidor"
        finally:
            if connection:
                connection.close()