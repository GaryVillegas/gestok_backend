from database.db_mysql import get_connection
from models.Users import Users
from flask_bcrypt import Bcrypt  # Para encriptar contraseñas de forma segura
from flask_jwt_extended import create_access_token, create_refresh_token

class AuthService:
    """
    Servicio de autenticación que maneja la lógica de negocio
    para registro, login y gestión de usuarios
    """

    @classmethod
    def register_user(cls, email: str, password: str):
        """ 
        Registra un nuevo usuario en la base de datos
        
        Args:
            email (str): Correo electrónico del usuario
            password (str): Contraseña en texto plano
            
        Returns:
            tuple: (Usuario objeto, mensaje) o (None, mensaje de error)
        """ 
        connection = None
        try:
            # Obtener conexión a la base de datos
            connection = get_connection()
            with connection.cursor() as cursor:
                # Verifica si el usuario ya existe en la base de datos
                # Llama a un stored procedure para verificar el email
                cursor.execute("call sp_user_verification(%s)", (email,))
                # Equivalente a: SELECT id FROM users WHERE email = %s
                existing_user = cursor.fetchone()
                
                # Si el usuario ya existe, retornar error
                if existing_user:
                    return None, "El usuario ya existe"
                
                # Encriptar la contraseña antes de guardarla por seguridad
                # Bcrypt es un algoritmo de hashing seguro para contraseñas
                bcrypt = Bcrypt()  # Crear instancia de Bcrypt
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                
                # Insertar nuevo usuario en la base de datos
                # Llama a un stored procedure para registrar el usuario
                cursor.execute("call sp_register_user(%s, %s)", (email, hashed_password))
                # Equivalente a: INSERT INTO users(email, password) VALUES (%s, %s)
                
                # Obtener el ID del usuario recién creado
                user_data = cursor.fetchone()# Obtiene el resultado del stored procedure
                user_id = user_data[0]
                
                # Confirmar la transacción en la base de datos
                connection.commit()
                
                # Crear el objeto usuario con los datos obtenidos
                user = Users(user_id, email, hashed_password)
                return user, "Usuario registrado exitosamente"
                
        except Exception as ex:
            # Manejo de errores: log del error y rollback de la transacción
            print(f'Exception. Type {type(ex)}: {str(ex)}')
            if connection:
                connection.rollback()  # Revertir cambios en caso de error
            return None, "Error en el servidor"
        finally:
            # Cerrar la conexión a la base de datos siempre
            if connection:
                connection.close()

    @classmethod
    def authenticate_user(cls, email: str, password: str):
        """ 
        Autentica un usuario y genera tokens JWT si las credenciales son válidas
        
        Args:
            email (str): Correo electrónico del usuario
            password (str): Contraseña en texto plano
            
        Returns:
            tuple: (Diccionario con datos del usuario y tokens, mensaje) o (None, mensaje de error)
        """ 
        connection = None
        try:
            connection = get_connection()
            with connection.cursor() as cursor:
                # Buscar usuario por email en la base de datos
                cursor.execute("call sp_search_by_email(%s)", (email,))
                # Equivalente a: "SELECT id, email, password FROM users WHERE email = %s"
                row = cursor.fetchone()
                
                # Si no se encuentra el usuario, retornar error
                if row is None:
                    return None, "Credenciales inválidas"
                    
                # Extraer datos del usuario desde la fila obtenida
                user_id, user_email, hashed_password = row
                
                # Verificar si la contraseña proporcionada coincide con el hash almacenado
                bcrypt = Bcrypt()  # Crear instancia de Bcrypt para verificación
                if bcrypt.check_password_hash(hashed_password, password):
                    # Contraseña válida - generar tokens JWT
                    
                    # Crear access token (token de acceso de corta duración)
                    # Se convierte user_id a string para compatibilidad con JWT
                    access_token = create_access_token(identity=str(user_id))
                    
                    # Crear refresh token (token de actualización de larga duración)
                    refresh_token = create_refresh_token(identity=str(user_id))
                    
                    # Crear objeto usuario
                    user = Users(user_id, user_email, hashed_password)
                    
                    # Retornar datos del usuario y tokens
                    return {
                        'user': user.to_dict(),          # Datos del usuario en formato diccionario
                        'access_token': access_token,    # Token para acceder a rutas protegidas
                        'refresh_token': refresh_token   # Token para renovar el access token
                    }, "Login exitoso"
                else:
                    # Contraseña incorrecta
                    return None, "Credenciales inválidas"
                    
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
    def get_user_by_id(cls, user_id):
        """
        Obtiene un usuario por su ID (útil para verificar tokens JWT)
        
        Args:
            user_id: Identificador del usuario
            
        Returns:
            Users: Objeto usuario si existe, None si no se encuentra
        """
        connection = None
        try:
            # Obtener conexión a la base de datos
            connection = get_connection()
            with connection.cursor() as cursor:
                # Buscar usuario por ID usando stored procedure
                cursor.execute("call sp_get_user_by_id(%s)", (user_id,))
                # Equivalente a: "SELECT id, email, password FROM users WHERE id = %s"
                row = cursor.fetchone()
                # Si se encuentra el usuario, crear y retornar objeto Users
                if row:
                    return Users(row[0], row[1], row[2])  # id, email, password
                return None  # Usuario no encontrado
                
        except Exception as ex:
            # Manejo de errores en la consulta
            print(f'Exception. Type {type(ex)}: {str(ex)}')
            if connection:
                connection.rollback()
            return None
        finally:
            # Cerrar conexión siempre
            if connection:
                connection.close()