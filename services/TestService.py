#importamos la conexion a base de datos
from database.db_mysql import get_connection
#importamos el modelo de test
from models.Test import Test

class TestService():

    @classmethod
    def testInsert(cls, test):
        try:
            # Obtenemos la conexión a la base de datos
            connection = get_connection()
            created_test = []
            # Abrimos un cursor para ejecutar la consulta
            with connection.cursor() as cursor:
                # Ejecutamos el procedimiento almacenado para insertar un test
                cursor.execute("call sp_testInsert(%s)", (test.text))
                # Obtenemos la primera fila del resultado
                row = cursor.fetchone()
                # Si existe una fila, creamos una instancia del modelo Test
                if row != None:
                    created_test = Test(row[0], row[1], row[2])
                # Confirmamos la transacción
                connection.commit()
            # Cerramos la conexión a la base de datos
            connection.close()
            # Retornamos el test creado
            return created_test
        except Exception as ex:
            # Imprimimos el error en caso de excepción
            print( f'Exception. Type {type(ex)}: {str(ex)}' )

    @classmethod
    def testSelect(cls):
        try:
            #Obtenemos la conexión a la base de datos
            connection = get_connection()
            tests = []
            # Abrimos un cursor para ejecutar la consulta
            with connection.cursor() as cursor:
                # Ejecutamos el procedimiento almacenado para insertar un test
                cursor.execute("call sp_testSelect()")
                #Obtenemos los resultados
                rows = cursor.fetchall()
                #Si existen filas, creamos una instancia del modelo Test por cada una
                if rows:
                    for row in rows:
                        tests.append(Test(row[0], row[1], row[2]))
                #confirmamos la transacción
                connection.commit()
            #Cerramos la conexión a la base de datos
            connection.close()
            #Retornamos la lista de tests creados
            return tests
        except Exception as ex:
            #Imprimimos el error en caso de excepción
            print(f'Exception. Type {type(ex)}: {str(ex)}')