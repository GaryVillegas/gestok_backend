from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, create_access_token, set_access_cookies, set_refresh_cookies, unset_jwt_cookies
)
from services.AuthService import AuthService

# Crear Blueprint para rutas de autenticación
# Un Blueprint permite organizar rutas relacionadas en módulos
auth_bp = Blueprint('auth_routes', __name__)

# Ruta para registrar nuevos usuarios
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Ruta para registrar nuevos usuarios
    """
    try:
        # Obtener datos del request en formato JSON
        email = request.json.get('email', None).strip().lower()
        password = request.json.get('password', None)
        
        # Validar que se proporcionen todos los datos necesarios
        if not email or not password:
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400
        
        # Registrar usuario mediante el servicio de autenticación
        user, message = AuthService.register_user(email, password)
        
        # Si el usuario fue creado exitosamente
        if user:
            return jsonify({'message': message, 'user': user.to_dict()}), 201
        else:
            return jsonify({'message': message}), 400
            
    except Exception as ex:
        # Manejar cualquier error inesperado del servidor
        return jsonify({'Error': 'Error interno del servidor'}), 500

# Ruta para autenticar usuarios y generar tokens JWT
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Ruta para autenticar usuarios y generar tokens jwt
    """
    try:
        # Obtener credenciales del request
        email = request.json.get('email', None).strip().lower()
        password = request.json.get('password', None)
        
        # Validar que se proporcionen las credenciales
        if not email or not password:
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400
        
        # Autenticar usuario mediante el servicio
        result, message = AuthService.authenticate_user(email, password)
        
        # Si la autenticación es exitosa
        if result:
            # Crear respuesta JSON con tokens e información del usuario
            response = jsonify({
                'message': message, 
                'access_token': result['access_token'],
                'refresh_token': result['refresh_token'],
                #'user': result['user']
            })

            # Establecer cookies HTTP-Only para los tokens
            # Esto mejora la seguridad previniendo acceso desde JavaScript
            set_access_cookies(response, result['access_token'])
            set_refresh_cookies(response, result['refresh_token'])
            return response, 200
        else:
            # Credenciales inválidas
            return jsonify({'error': message}), 401
            
    except Exception as ex:
        # Log del error para debugging
        print(f"Error en login: {str(ex)}")
        return jsonify({'Error': 'Error interno del servidor'}), 500

# Ruta para generar un nuevo access token usando el refresh token
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)  # Requiere un refresh token válido en la solicitud
def refresh():
    """
    Ruta para generar un nuevo access token usando el refresh token
    """
    try:
        # Obtener la identidad del usuario desde el token JWT
        current_user_id = get_jwt_identity()
        
        # Asegurar que user_id sea string para consistencia
        current_user_id = str(current_user_id)
        
        # Verificar que el usuario aún existe en la base de datos
        user = AuthService.get_user_by_id(current_user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        # Crear nuevo access token con la misma identidad
        new_access_token = create_access_token(identity=current_user_id)
        
        # Preparar respuesta y establecer cookie con el nuevo token
        response = jsonify({'message': 'Token refrescado'})
        set_access_cookies(response, new_access_token)
        return response, 200
        
    except Exception as ex:
        # Log del error para debugging
        print(f"Error en refresh: {str(ex)}")
        return jsonify({'error': 'Error al refrescar token'}), 500

# Ruta protegida que requiere autenticación
@auth_bp.route('/protected', methods=['GET'])
@jwt_required()  # Requiere un access token válido para acceder
def protected():
    """
    Ruta protegida que requiere autenticación
    Ejemplo de cómo proteger rutas con JWT
    """
    try:
        # Obtener el ID del usuario desde el token JWT
        current_user_id = get_jwt_identity()
        
        # Obtener información completa del usuario desde la base de datos
        user = AuthService.get_user_by_id(current_user_id)
        
        if user:
            # Usuario válido, permitir acceso a la ruta protegida
            return jsonify({
                'message': 'Acceso permitido a ruta protegida', 
                'user': user.to_dict()
            }), 200
        else:
            # Usuario no encontrado (posiblemente eliminado)
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
    except Exception as ex:
        # Error en la autenticación
        return jsonify({'error': 'Error de autenticación'}), 401

# Ruta para cerrar sesión
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()  # Requiere que el usuario esté autenticado para hacer logout
def logout():
    """
    Ruta para cerrar sesión del usuario
    
    En JWT, el logout se maneja principalmente en el cliente descartando los tokens,
    pero en el servidor podemos implementar medidas adicionales de seguridad.
    """
    try:
        # Obtener la identidad del usuario desde el token JWT
        current_user_id = get_jwt_identity()
        
        # En una implementación básica, simplemente creamos una respuesta de éxito
        response = jsonify({
            'message': 'Logout exitoso. Por favor, elimine los tokens del cliente.'
        }), 200
        
        # Opcional: Limpiar las cookies HTTP-Only si se estaban usando
        # Esto asegura que el cliente no pueda reutilizar las cookies
        response = jsonify({'message': 'Logout exitoso'})
        unset_jwt_cookies(response)  # Elimina todas las cookies JWT
        # Alternativamente se pueden eliminar individualmente:
        # unset_access_cookies(response)
        # unset_refresh_cookies(response)
        
        # EN UNA IMPLEMENTACIÓN AVANZADA SE HARÍA LO SIGUIENTE:
        
        # 1. Obtener el token actual del request
        # from flask_jwt_extended import get_jwt
        # current_token = get_jwt()
        
        # 2. Agregar el token a una lista negra (blacklist) en la base de datos
        # para prevenir que sea reutilizado antes de su expiración
        # AuthService.add_token_to_blacklist(current_token['jti'], current_token['exp'])
        
        # 3. Opcional: Registrar el evento de logout para auditoría
        # AuthService.log_logout_event(current_user_id)
        
        return response
    except Exception as ex:
        # Log del error para debugging
        print(f"Error en logout: {str(ex)}")
        return jsonify({'error': 'Error durante el logout'}), 500

# Ruta para obtener información del usuario actualmente autenticado
@auth_bp.route('/me', methods=['GET'])
@jwt_required()  # Requiere autenticación
def get_current_user():
    """
    Ruta para obtener información del usuario actualmente autenticado
    """
    try:
        # Obtener el ID del usuario desde el token JWT
        current_user_id = get_jwt_identity()
        
        # Obtener información completa del usuario
        user = AuthService.get_user_by_id(current_user_id)
        
        if user:
            # Devolver información del usuario en formato JSON
            return jsonify({'user': user.to_dict()}), 200
        else:
            # Usuario no encontrado en la base de datos
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
    except Exception as ex:
        # Error al procesar la solicitud
        return jsonify({'error': 'Error al obtener usuario'}), 500