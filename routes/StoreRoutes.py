from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.StoreService import StoreService

#Creamos Blueprint para rutas de tienda
store_bp = Blueprint('store_routes', __name__)

#Ruta para registrar una nueva tienda
@store_bp.route('/create', methods=['POST'])
@jwt_required()
def create_store():
    """
    Ruta para registrar una nueva tienda
    """
    try:
        #Obtener datos del rrequest en formato JSON
        store = {
            'description': request.json.get('description', None),
            'address': request.json.get('address', None)
        }
        #Obtener la identidad del usuario via JWT
        current_user_id = int(get_jwt_identity())

        if not store['description'] or not store['address'] or not current_user_id:
            return jsonify({'error': 'Los datos son requeridos.'}), 400
        
        store_id, message = StoreService.create_store(store, current_user_id)
        if store_id:
            return jsonify({'message': message, 'store_id': store_id}), 200
        
        return jsonify({'message': message}), 400
    except Exception as ex:
        #Manejar errores
        print(f"Error en creación: {str(ex)}")
        return jsonify({'Error': 'Error interno del servidor'}), 500
    
@store_bp.route('/mystore', methods = ['GET'])
@jwt_required()
def store():
    """
    Ruta para traer tienda de usuario
    """
    try:
        current_user_id = int(get_jwt_identity())
        if not current_user_id:
            return jsonify({'error': 'usuario no encontrado.'}), 400
        
        user_store, message = StoreService.get_store(current_user_id)
        if user_store:
            return jsonify({'message': message, 'store': user_store.to_dict()})
        
        return jsonify({'message': message}), 400
    except Exception as ex:
        print(f"Error al traer tienda: {str(ex)}")
        return jsonify({'Error': 'Error interno del servidor'}), 500
    
@store_bp.route('/delete/<int:store_id>', methods=['DELETE'])
@jwt_required()
def delete_store(store_id: int):
    """
    Ruta para poder eliminar tienda
    """
    try:
        if not store_id:
            return jsonify({'error': 'tienda no encontrada.'}), 400
        
        row_affected, message = StoreService.delete_store(store_id)
        if row_affected is not None and row_affected > 0:
            return jsonify({'message': message, 'row_affected': row_affected}), 200
        
        return jsonify({'message': message}), 400
    except Exception as ex:
        print(f"Error al eliminar cuenta. Type {str(type)}: {str(ex)}")
        return jsonify({'Error': 'Error interno del servidor'}), 500