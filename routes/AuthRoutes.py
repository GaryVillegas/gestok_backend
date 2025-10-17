from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, create_access_token, 
    create_refresh_token, set_access_cookies, set_refresh_cookies,
    unset_jwt_cookies, unset_access_cookies, unset_refresh_cookies
)
from services.AuthService import AuthService

#Crear Blueprint para rutas de autenticacion
auth_bp = Blueprint('auth_routes', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Ruta para registrar nuevos usuarios
    """
    try:
        #Obtener datos del request
        email = request.json.get('email', None)
        password = request.json.get('password', None)
        #Validar que se proporcionen todos los datos necesarios
        if not email or not password:
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400
        #Registrar usuario
        user, message = AuthService.register_user(email, password)
        if user:
            return jsonify({'message': message, 'user': user.to_dict()}), 201
        else:
            return jsonify({'message': message}), 400
    except Exception as ex:
        return jsonify({'Error': 'Error interno del servidor'}), 500
    
@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Ruta para autenticar usuarios y generar tokens jwt
    """
    try:
        # Obtener credenciales del request
        email = request.json.get('email', None)
        password = request.json.get('password', None)
        # Validar Credenciales
        if not email or not password:
            return jsonify({'error': 'Email y contraseña son requeridos'}), 400
        # Autenticar usuario - CORREGIDO: sintaxis correcta
        result, message = AuthService.authenticate_user(email, password)
        if result:
            response = jsonify({
                'message': message, 
                'access_token': result['access_token'],
                'refresh_token': result['refresh_token'],
                'user': result['user']
            })

            # Establecer cookies HTTP-Only
            set_access_cookies(response, result['access_token'])
            set_refresh_cookies(response, result['refresh_token'])
            return response, 200
        else:
            return jsonify({'error': message}), 401
    except Exception as ex:
        print(f"Error en login: {str(ex)}")
        return jsonify({'Error': 'Error interno del servidor'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True) # Requiere un refresh token válido
def refresh():
    """
    Ruta para generar un nuevo access token usando el refresh token
    """
    try:
        current_user_id = get_jwt_identity()
        # CORREGIDO: Asegurar que user_id sea string
        current_user_id = str(current_user_id)
        # Verificar que el usuario aún existe
        user = AuthService.get_user_by_id(current_user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404  # CORREGIDO: llaves no corchetes
        # Crear nuevo access token
        new_access_token = create_access_token(identity=current_user_id)
        response = jsonify({'message': 'Token refrescado'})  # CORREGIDO: llaves no corchetes
        set_access_cookies(response, new_access_token)
        return response, 200
    except Exception as ex:
        print(f"Error en refresh: {str(ex)}")  # CORREGIDO: f-string
        return jsonify({'error': 'Error al refrescar token'}), 500  # CORREGIDO: llaves no corchetes
    
@auth_bp.route('/protected', methods=['GET'])
@jwt_required() #Requiere un access token valido
def protected():
    """
    Ruta protegida que requiere autenticación
    Ejemplo de cómo proteger rutas con JWT
    """
    try:
        #Obtener el ID del usuario desde el token
        current_user_id = get_jwt_identity()
        #Obtener información del usuario
        user = AuthService.get_user_by_id(current_user_id)
        if user:
            return jsonify({'message': 'Acceso permitido a ruta protegida', 'user': user.to_dict()}), 200
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
    except Exception as ex:
        return jsonify({'error': 'Error de autenticación'}), 401
    
@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Ruta para logout (en JWT normalmente se maneja en el cliente)
    Pero podemos validar el token si usamos una backlist
    """
    #En una implementación avanzada, agregaremos token blacklist
    return jsonify({'message': 'Logout exitoso'}), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Ruta para obtener información del usuario actualmente autenticado
    """
    try:
        current_user_id = get_jwt_identity()
        user = AuthService.get_user_by_id(current_user_id)
        if user:
            return jsonify({'user': user.to_dict()}), 200
        else:
            return jsonify({'error': 'Usuario no encontrado'}), 404
    except Exception as ex:
        return jsonify({'error': 'Error al obtener usuario'}), 500