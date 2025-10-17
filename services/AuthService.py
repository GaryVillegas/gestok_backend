from database.db_mysql import get_connection
from models.Users import Users
from flask_bcrypt import Bcrypt  # Para encriptar contraseñas
from flask_jwt_extended import create_access_token, create_refresh_token

class AuthService:

    @classmethod
    def register_user(cls, email: str, password: str):
        """
        Registra un nuevo usuario en la base de datos
        """
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                #Verifica si el usuario ya existe
                cursor.execute("call sp_user_verification(%s)", (email,))
                #SELECT id FROM users WHERE email = %s
                existing_user = cursor.fetchone()
                if existing_user:
                    return None, "El usuario ya existe"
                #Encriptar la contrasenna antes de guardarla
                hashed_password = Bcrypt.generate_password_hash(password).decode('utf-8')
                #Insertar nuevo usuario
                cursor.execute("call sp_register_user(%s, %s)", (email, hashed_password))
                #INSERT INTO users(email, password) VALUES (%s, %s)
                user_id = cursor.fetchon()
                connection.commit()
                #Crear el objeto usuario
                user = Users(user_id, email, hashed_password)
                return user, ("Usuario registrado exitosamente")
        except Exception as ex:
            print(f'Exception. Type {type(ex)}: {str(ex)}')
            if connection:
                connection.rollback()
            return None, "Error en el servidor"
        finally:
            if connection:
                connection.close()

    @classmethod
    def authenticate_user(cls, email: str, password: str):
        """
        Autentica un usuario y genera tokens JWT si las credenciales son validas
        """
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                #Buscar usuario por email
                cursor.execute("call search_by_email(%s)", (email,))
                #"SELECT id, email, password FROM users WHERE email = %s"
                row = cursor.fetchone()
                if row is None:
                    return None, "Credenciales invalidas"
                user_id, user_email, hashed_password = row
                #Verificar contrasenna
                if Bcrypt.check_password_hash(hashed_password, password):
                    #Crear tokens JWT
                    accses_token = create_access_token(identity=user_id)
                    refresh_token = create_refresh_token(identity=user_id)
                    user = Users(user_id, user_email, hashed_password)
                    return {
                        'user': user.to_dict(),
                        'access_token': accses_token,
                        'refresh_token': refresh_token
                    }, "Login existoso"
                else:
                    return None, "Credenciales invalidas"
        except Exception as ex:
            print(f'Exception. Type {type(ex)}: {str(ex)}')
            if connection:
                connection.rollback()
                return None, "Error en el servidor"
        finally:
            if connection:
                connection.close()

    @classmethod
    def get_user_by_id(cls, user_id):
        """
        Obtiene un usuario por su ID (util para verificar tokens)
        """
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute("call sp_get_user_by_id(%s)", (user_id,))
                #"SELECT id, email, password FROM users WHERE id = %s"
                row = cursor.fetchone()
                if row:
                    return Users(row[0], row[1], row[2])
                return None
        except Exception as ex:
            print(f'Exception. Type {type(ex)}: {str(ex)}')
            if connection:
                connection.rollback()
            return None
        finally:
            if connection:
                connection.close()