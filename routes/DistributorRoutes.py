from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from services.DistributorService import DistributorService

distributor_bp = Blueprint('distributor_routes', __name__)

@distributor_bp.route('/create', methods=['POST'])
@jwt_required()
def create_distributor():
    """
    Ruta para crear distribuidor
    """
    try:
        distributor = {
            'description': request.json.get('description', None)
        }
        current_user_id = int(get_jwt_identity())
        if not current_user_id or not distributor['description']:
           return jsonify({'error': 'Los datos son requeridos.'}), 400
        
        distributor_id, message = DistributorService.create_distributor(distributor, current_user_id)
        if distributor_id:
            return jsonify({'message': message, 'distributor_id': distributor_id}), 200
        
        return jsonify({'message': message}), 400
    except Exception as ex:
        print(f"Error en creacion: {str(ex)}")
        return jsonify({'Error': 'Error interno del servidor'}), 500
    
@distributor_bp.route('/distributors', methods=['GET'])
@jwt_required()
def distributors():
    """
    Ruta para traer distribuidores de usuario
    """
    try:
        current_user_id = int(get_jwt_identity())
        if not current_user_id:
            return jsonify({'error': 'usuario no encontrado'}), 400
        
        distributors, message = DistributorService.get_distributor(current_user_id)
        if distributors:
            distributors_dict = [distributor.to_dict() for distributor in distributors]
            return jsonify({'message': message, 'distributors': distributors_dict}), 200

        return jsonify({'message': message}), 404
    except Exception as ex:
        print(f"Error al obtener distribuidores: {str(ex)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@distributor_bp.route('/delete/<int:distributor_id>', methods=['DELETE'])
@jwt_required()
def delete_distributor(distributor_id: int):
    """
    Ruta para eliminar distribuidor
    """
    try:
        if not distributor_id:
            return jsonify({'error': 'distribuidor no encontrado.'}), 404
        
        row_affected, message = DistributorService.delete_distributor(distributor_id)
        if row_affected is not None and row_affected > 0:
            return jsonify({'message': message, 'row_affected': row_affected}), 200
        
        return jsonify({'message': message})
    except Exception as ex:
        print(f"Error al eliminar distribuidor. type{str(type)}: {str(ex)}")
        return jsonify({'Error': 'Error interno del servidor'}), 500