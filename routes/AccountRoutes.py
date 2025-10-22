from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.AccountService import AccountService

#Crear Blueprint para rutas de autenticación
#Un Blueprint permite organizar rutas relacionadas en módulos
account_bp = Blueprint('account_routes', __name__)

#Ruta para registrar nueva cuenta de usuario
@account_bp.route('/register', methods=['POST'])
@jwt_required()
def register_account():
    """
    Ruta para registrar cuenta de usuario
    """
    try:
        #Obtener datos del rrequest en formato JSON
        account = {
            'name': request.json.get('name', None),
            'lastname': request.json.get('lastname', None),
            'rut': request.json.get('rut', None)
        }
        #Obenter la identidad del usuario con JWT
        current_user_id = get_jwt_identity()
        current_user_id = int(current_user_id)

        #Validar que se proporcionen todos los datos necesario
        if not account['name'] or not account['lastname'] or not account['rut'] or not current_user_id:
            return jsonify({'error': 'Los datos son requeridos.'}), 400
        
        #Registrar cuenta de usuairo
        account_id, message = AccountService.create_account(account, current_user_id)
        if account_id:
            return jsonify({'message': message, 'account_id': account_id}), 200
        
        return jsonify({'message': message}), 400
    except Exception as ex:
        #Manejar errores
        print(f"Error en creación: {str(ex)}")
        return jsonify({'Error': 'Error interno del servidor'}), 500

@account_bp.route('/myaccount', methods=['GET'])
@jwt_required()
def account():
    """
    Ruta para traer cuenta de usuario
    """
    #Esta dando error 400.
    """Era problema del sp, estaba devolviendo 4 valores y esperamos 3."""
    try:
        current_user_id = int(get_jwt_identity())
        if not current_user_id:
            return jsonify({'error': 'usuario no encontrado.'}), 400
        
        user_account, message = AccountService.get_account(current_user_id)
        if user_account:
            return jsonify({'message': message, 'account': user_account.to_dict()}), 200
        
        return jsonify({'message': message}), 400
    except Exception as ex:
        print(f"Error al traer cuenta: {str(ex)}")
        return jsonify({'Error': 'Error interno del servidor'}), 500
    
@account_bp.route('/myaccount/delete', methods=['DELETE'])
@jwt_required()
def delete_account():
    """
    Ruta para eliminar cuenta
    """
    try:
        current_user_id = int(get_jwt_identity())
        if not current_user_id:
            return jsonify({'Error': 'Error al elimnar usuario.'}), 400
        
        row_affected, message = AccountService.delete_account(current_user_id)
        if row_affected is not None and row_affected > 0:
            return jsonify({'message': message, 'row affected': row_affected}), 201
        
        return jsonify({'message': message}), 400
    except Exception as ex:
        print(f"Error al eliminar cuenta: {str(ex)}")
        return jsonify({'Error': 'Error interno del servidor'}), 500