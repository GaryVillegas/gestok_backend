from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
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
            return jsonify({'error': 'Email y contrasenna son requeridos'}), 400
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
        #Obtener credenciales del request
        email = request.json.get('email', None)
        password = request.json.get('password', None)
        #Validar Credenciales
        if not email or not password:
            return jsonify({'error': 'Email y contrasenna son requeridos'}), 400
        #Autenticar usuario
        result, message = AuthService.authenticate_user(email, password)
        if result:
            return jsonify({'message': message, 'access_token': result['access_token'], 'refresh_token': result['refresh_token'], 'user': result['user']}), 200
        else:
            return jsonify({'error': message}), 401
    except Exception as ex:
        return jsonify({'Error': 'Error interno del servidor'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True) # Requiere un refresh token válido
def refresh():
    """
    Ruta para generar un nuevo access token usando el refresh token
    """
    try:
        current_user_id = get_jwt_identity()
        # Verificar que el usuario aún existe
        user = AuthService.get_user_by_id(current_user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        # Crear nuevo access token
        from flask_jwt_extended import create_access_token
        new_access_token = create_access_token(identity=current_user_id)
        return jsonify({
            'access_token': new_access_token
        }), 200
    except Exception as ex:
        return jsonify({'error': 'Error al refrescar token'}), 500
    
#TODO: https://chat.deepseek.com/share/66ag69uyvbzn74t1f1