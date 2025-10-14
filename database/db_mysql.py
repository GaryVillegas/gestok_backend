from dotenv import load_dotenv #importamos load_dotenv desde python-dotenv module
import os #nos da acceso a OS y nos ayuda a leer las variables de entorno
load_dotenv() #cargamos el env
import pymysql #importamos la librería de mysql

#Creamos un diccionario de datos
HOST = os.getenv("MYSQL_HOST")
USER = os.getenv("MYSQL_USER")
PASSWORD = os.getenv("MYSQL_PASSWORD")
DATABASE = os.getenv("MYSQL_DB")

def get_connection():
    try:
        return pymysql.connect(
            host=HOST,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
    except Exception as ex:
        raise ex