from database.db_mysql import get_connection
from models.Category import Category

class CategoryServie:
    """
    Clase para manejar el negocio de categorias en productos.
    """
    @classmethod
    def create_category(cls, category, user_id: int):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("call sp_create_category(%s, %s)", (category['description'], user_id,))
                row = cursor.fetchone()
                if row is None:
                    return None, "Error al crear categoria."
                
                category_id = row[0]
                connection.commit()
                return category_id, "Categoria creada con exito."
        except Exception as ex:
            print(f"Exception. Type {str(type)}: {str(ex)}")
            if connection:
                connection.rollback()
            return None, "Erro en el servidor"
        finally:
            if connection: connection.close()
    
    @classmethod
    def get_categories(cls, user_id: int):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("call sp_get_categories(%s)", (user_id, ))
                rows = cursor.fetchall()
                if rows is None:
                    return None, "No se encontraron categorias."
                
                categories = [
                    Category(row[0], row[1], user_id)
                    for row in rows
                ]

                return categories, "Se encontraron categorias."
        except Exception as ex:
            print(f"Exception. Type{str(type)}: {str(ex)}")
            if connection:
                connection.rollback()
            return None, "Eror en el servidor"
        finally:
            if connection:
                connection.close()
    
    @classmethod
    def delete_category(cls, category_id: int):
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("call sp_delete_category(%s)", (category_id,))
                row = cursor.fetchone()
                connection.commit()
                if row:
                    row_affected = row[0]
                    if row_affected > 0:
                        return row_affected, "Se elimino la categoria."
                    else:
                        return 0, "No se encontraron datos para eliminar."
                
                return 0, "Error al eliminar categoria"
        except Exception as ex:
            print(f"Exception. Type{str(type)}: {str(ex)}")
            if connection:
                connection.rollback()
            return None, "Error en el servidor"
        finally:
            if connection:
                connection.close()